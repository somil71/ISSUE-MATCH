SKILL_OVERLAP_WEIGHT = 0.40
BLAST_RADIUS_WEIGHT = 0.35
GAP_PENALTY_WEIGHT = 0.25


def compute_readiness(
    skill_overlap_ratio: float, avg_blast_radius_score: float, gap_size: int
) -> float:
    """Gap penalty is an absolute count (1/(1+gap_size)), not a ratio, since
    skill_overlap_ratio is already a required-skills fraction and a second
    ratio term would just double-count it under a different weight."""
    gap_set_size_penalty = 1 / (1 + gap_size)
    return (
        SKILL_OVERLAP_WEIGHT * skill_overlap_ratio
        + BLAST_RADIUS_WEIGHT * (1 - avg_blast_radius_score)
        + GAP_PENALTY_WEIGHT * gap_set_size_penalty
    )
