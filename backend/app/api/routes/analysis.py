import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.auth import get_current_user
from app.core.security import decrypt_token
from app.db.models import User
from app.services import (
    analysis_cache,
    call_graph,
    churn,
    code_owners,
    dependency_graph,
    github_client,
    repo_fetcher,
    skill_gap,
    test_proximity,
)
from app.services.blast_radius import compute_blast_radius
from app.services.blast_radius_summary import summarize
from app.services.complexity import cyclomatic_complexity
from app.services.parsing.engine import parse_file
from app.services.parsing.languages import LANGUAGES
from app.services.readiness import compute_readiness

router = APIRouter()

_ALL_EXTENSIONS = {ext for spec in LANGUAGES.values() for ext in spec.extensions}
_MAX_TRANSITIVE_HOPS = 6


@router.post("/repos/{owner}/{name}/analyze")
async def analyze_repo(owner: str, name: str, user: User = Depends(get_current_user)) -> dict:
    full_name = f"{owner}/{name}"
    access_token = decrypt_token(user.encrypted_access_token)

    try:
        repo_meta = await github_client.fetch_repo(full_name, access_token)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail="Could not fetch repo from GitHub"
        ) from exc

    try:
        repo_path = repo_fetcher.clone_repo(full_name)
    except repo_fetcher.RepoFetchError as exc:
        raise HTTPException(status_code=502, detail=f"Could not clone repo: {exc}") from exc

    commit_sha = repo_fetcher.current_commit_sha(repo_path)
    source_files = repo_fetcher.list_source_files(repo_path, _ALL_EXTENSIONS)

    parsed_files = []
    for path in source_files:
        relative_path = str(path.relative_to(repo_path))
        parsed = parse_file(path, relative_path)
        if parsed:
            parsed_files.append(parsed)

    fan_in_metrics = call_graph.build_fan_in(parsed_files)
    complexity_by_id = {
        fid: cyclomatic_complexity(fm.function.node, fm.function.source, fm.function.language)
        for fid, fm in fan_in_metrics.items()
    }
    tested_names = test_proximity.build_tested_names(parsed_files)

    try:
        churn_by_file = churn.compute_file_churn(repo_path)
    except churn.ChurnError:
        churn_by_file = {}

    try:
        owners_by_file = code_owners.compute_file_owners(repo_path)
    except code_owners.CodeOwnersError:
        owners_by_file = {}

    blast_radius = compute_blast_radius(fan_in_metrics, complexity_by_id, tested_names, churn_by_file)

    call_graph_data = dependency_graph.build_call_graph(parsed_files)
    transitive_fan_in_by_id = {
        fid: len(
            dependency_graph.transitive_dependents(fid, call_graph_data, max_hops=_MAX_TRANSITIVE_HOPS)
        )
        for fid in fan_in_metrics
    }

    functions = [
        {
            "id": fid,
            "name": fm.function.name,
            "file": fm.function.relative_path,
            "start_line": fm.function.start_line,
            "end_line": fm.function.end_line,
            "fan_in": fm.fan_in,
            "transitive_fan_in": transitive_fan_in_by_id[fid],
            "name_is_ambiguous": fm.name_is_ambiguous,
            "cyclomatic_complexity": complexity_by_id[fid],
            "has_test_coverage": blast_radius[fid].has_test_coverage,
            "churn_intensity": round(blast_radius[fid].churn_intensity, 4),
            "normalized_fan_in": round(blast_radius[fid].normalized_fan_in, 4),
            "normalized_complexity": round(blast_radius[fid].normalized_complexity, 4),
            "normalized_churn": round(blast_radius[fid].normalized_churn, 4),
            "blast_radius_score": round(blast_radius[fid].score, 4),
            "bucket": blast_radius[fid].bucket,
            "summary": summarize(blast_radius[fid]),
        }
        for fid, fm in fan_in_metrics.items()
    ]
    functions.sort(key=lambda f: f["blast_radius_score"], reverse=True)

    owners_payload = {
        file: {"author": owner.author, "commit_count": owner.commit_count}
        for file, owner in owners_by_file.items()
    }
    await analysis_cache.store_analysis(full_name, commit_sha, functions, owners_payload)
    graph_edges = {
        caller_id: sorted(callee_ids) for caller_id, callee_ids in call_graph_data.edges.items()
    }
    await analysis_cache.store_graph(full_name, commit_sha, functions, graph_edges)

    try:
        inferred_languages = await github_client.fetch_user_repo_languages(
            user.username, access_token
        )
    except httpx.HTTPStatusError:
        inferred_languages = []

    required_skills = skill_gap.extract_required_skills(repo_path)
    gap = skill_gap.compute_gap(required_skills, [*user.skills, *inferred_languages])

    skill_overlap_ratio = (
        len(gap["have"]) / len(gap["required"]) if gap["required"] else 1.0
    )
    avg_blast_radius_score = (
        sum(f["blast_radius_score"] for f in functions) / len(functions) if functions else 0.0
    )
    readiness_score = compute_readiness(
        skill_overlap_ratio=skill_overlap_ratio,
        avg_blast_radius_score=avg_blast_radius_score,
        gap_size=len(gap["gap"]),
    )

    return {
        "repo": full_name,
        "commit_sha": commit_sha,
        "default_branch": repo_meta.get("default_branch"),
        "file_count": len(parsed_files),
        "function_count": len(functions),
        "functions": functions,
        "skill_gap": gap,
        "avg_blast_radius_score": round(avg_blast_radius_score, 4),
        "readiness_score": round(readiness_score, 4),
    }
