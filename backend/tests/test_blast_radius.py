from pathlib import Path

from app.services.blast_radius import compute_blast_radius
from app.services.call_graph import build_fan_in
from app.services.churn import FileChurn
from app.services.complexity import cyclomatic_complexity
from app.services.parsing.engine import parse_file


def test_blast_radius_buckets_high_and_low_risk_functions(tmp_path: Path) -> None:
    source = """
def risky(x):
    if x:
        if x > 1:
            return 1
        elif x > 2:
            return 2
    return 0

def safe():
    return 1

def caller():
    risky(1)
    risky(2)
    risky(3)
    safe()
"""
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    fan_in_metrics = build_fan_in([parsed])
    complexity_by_id = {
        fid: cyclomatic_complexity(fm.function.node, fm.function.source, fm.function.language)
        for fid, fm in fan_in_metrics.items()
    }
    tested_names = frozenset({"safe"})
    churn_by_file = {"sample.py": FileChurn(commit_count=50, days_since_last_commit=1)}

    results = compute_blast_radius(
        fan_in_metrics, complexity_by_id, tested_names, churn_by_file
    )
    by_name = {fan_in_metrics[fid].function.name: fm for fid, fm in results.items()}

    assert by_name["risky"].bucket == "here_be_dragons"
    assert by_name["safe"].bucket == "start_here"
    assert by_name["risky"].score > by_name["safe"].score
    assert by_name["safe"].has_test_coverage
    assert not by_name["risky"].has_test_coverage


def test_blast_radius_handles_uniform_values_without_division_by_zero(
    tmp_path: Path,
) -> None:
    source = "def a():\n    return 1\n\ndef b():\n    return 2\n"
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    fan_in_metrics = build_fan_in([parsed])
    complexity_by_id = {fid: 1 for fid in fan_in_metrics}

    results = compute_blast_radius(fan_in_metrics, complexity_by_id, frozenset(), {})
    assert all(fm.score == results[next(iter(results))].score for fm in results.values())
