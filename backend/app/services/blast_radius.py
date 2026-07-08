from dataclasses import dataclass

from app.services.call_graph import FunctionMetrics
from app.services.churn import FileChurn

FAN_IN_WEIGHT = 0.35
COMPLEXITY_WEIGHT = 0.30
TEST_PROXIMITY_WEIGHT = 0.20
CHURN_WEIGHT = 0.15

BUCKET_THRESHOLD = 0.5


def _normalize(values: dict[str, float]) -> dict[str, float]:
    if not values:
        return {}
    lo, hi = min(values.values()), max(values.values())
    if hi == lo:
        return dict.fromkeys(values, 0.0)
    return {k: (v - lo) / (hi - lo) for k, v in values.items()}


@dataclass
class FunctionBlastRadius:
    function_id: str
    fan_in: int
    cyclomatic_complexity: int
    has_test_coverage: bool
    churn_intensity: float
    normalized_fan_in: float
    normalized_complexity: float
    normalized_churn: float
    score: float
    bucket: str  # "start_here" | "here_be_dragons"


def compute_blast_radius(
    fan_in_metrics: dict[str, FunctionMetrics],
    complexity_by_id: dict[str, int],
    tested_names: frozenset[str],
    churn_by_file: dict[str, FileChurn],
) -> dict[str, FunctionBlastRadius]:
    raw_fan_in = {fid: float(fm.fan_in) for fid, fm in fan_in_metrics.items()}
    raw_complexity = {fid: float(c) for fid, c in complexity_by_id.items()}
    raw_churn = {
        fid: churn_by_file[fm.function.relative_path].intensity
        if fm.function.relative_path in churn_by_file
        else 0.0
        for fid, fm in fan_in_metrics.items()
    }

    norm_fan_in = _normalize(raw_fan_in)
    norm_complexity = _normalize(raw_complexity)
    norm_churn = _normalize(raw_churn)

    results: dict[str, FunctionBlastRadius] = {}
    for fid, fm in fan_in_metrics.items():
        has_test = fm.function.name in tested_names
        score = (
            FAN_IN_WEIGHT * norm_fan_in[fid]
            + COMPLEXITY_WEIGHT * norm_complexity[fid]
            + TEST_PROXIMITY_WEIGHT * (0.0 if has_test else 1.0)
            + CHURN_WEIGHT * norm_churn[fid]
        )
        results[fid] = FunctionBlastRadius(
            function_id=fid,
            fan_in=fm.fan_in,
            cyclomatic_complexity=complexity_by_id[fid],
            has_test_coverage=has_test,
            churn_intensity=raw_churn[fid],
            normalized_fan_in=norm_fan_in[fid],
            normalized_complexity=norm_complexity[fid],
            normalized_churn=norm_churn[fid],
            score=score,
            bucket="start_here" if score < BUCKET_THRESHOLD else "here_be_dragons",
        )
    return results
