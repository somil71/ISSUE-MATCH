from pathlib import Path

from app.services.skill_gap import compute_gap, extract_required_skills


def test_extract_required_skills_from_requirements_txt(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("fastapi==0.115.6\nredis>=5.0\n# comment\n\n")

    skills = extract_required_skills(tmp_path)

    assert "Python" in skills
    assert "fastapi" in skills
    assert "redis" in skills


def test_extract_required_skills_from_package_json(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{"dependencies": {"react": "^18.0.0"}, "devDependencies": {"vite": "^5.0.0"}}'
    )
    (tmp_path / "tsconfig.json").write_text("{}")

    skills = extract_required_skills(tmp_path)

    assert "JavaScript" in skills
    assert "TypeScript" in skills
    assert "react" in skills
    assert "vite" in skills


def test_extract_required_skills_from_docker_and_pyproject(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["httpx>=0.28", "pydantic"]\n'
    )

    skills = extract_required_skills(tmp_path)

    assert "Docker" in skills
    assert "Python" in skills
    assert "httpx" in skills
    assert "pydantic" in skills


def test_extract_required_skills_dedupes_language_marker_against_manifest_entry(
    tmp_path: Path,
) -> None:
    (tmp_path / "package.json").write_text(
        '{"dependencies": {}, "devDependencies": {"typescript": "^5.0.0"}}'
    )
    (tmp_path / "tsconfig.json").write_text("{}")

    skills = extract_required_skills(tmp_path)

    typescript_variants = [s for s in skills if s.lower() == "typescript"]
    assert typescript_variants == ["TypeScript"]


def test_extract_required_skills_finds_manifest_in_subdirectory(tmp_path: Path) -> None:
    app_dir = tmp_path / "card"
    app_dir.mkdir()
    (app_dir / "package.json").write_text('{"dependencies": {"react": "^18.0.0"}}')

    skills = extract_required_skills(tmp_path)

    assert "JavaScript" in skills
    assert "react" in skills


def test_extract_required_skills_ignores_vendored_manifests(tmp_path: Path) -> None:
    vendored = tmp_path / "node_modules" / "some-dep"
    vendored.mkdir(parents=True)
    (vendored / "package.json").write_text('{"dependencies": {"leftpad": "^1.0.0"}}')

    skills = extract_required_skills(tmp_path)

    assert skills == set()


def test_extract_required_skills_prefers_shallowest_manifest(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"dependencies": {"top": "1.0.0"}}')
    nested = tmp_path / "packages" / "core"
    nested.mkdir(parents=True)
    (nested / "package.json").write_text('{"dependencies": {"nested": "1.0.0"}}')

    skills = extract_required_skills(tmp_path)

    assert "top" in skills
    assert "nested" not in skills


def test_compute_gap_is_case_insensitive_set_difference() -> None:
    required = {"Python", "FastAPI", "Docker", "redis"}
    user_skills = ["python", "fastapi"]

    result = compute_gap(required, user_skills)

    assert result["have"] == ["FastAPI", "Python"]
    assert result["gap"] == ["Docker", "redis"]
    assert result["required"] == ["Docker", "FastAPI", "Python", "redis"]
