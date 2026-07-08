from app.services.readiness import compute_readiness


def test_readiness_is_higher_for_better_skill_match_and_lower_risk() -> None:
    strong = compute_readiness(
        skill_overlap_ratio=1.0, avg_blast_radius_score=0.1, gap_size=0
    )
    weak = compute_readiness(
        skill_overlap_ratio=0.0, avg_blast_radius_score=0.9, gap_size=10
    )

    assert strong > weak
    assert 0 <= weak <= 1
    assert 0 <= strong <= 1


def test_readiness_gap_penalty_decreases_with_larger_gap() -> None:
    small_gap = compute_readiness(
        skill_overlap_ratio=0.5, avg_blast_radius_score=0.5, gap_size=1
    )
    large_gap = compute_readiness(
        skill_overlap_ratio=0.5, avg_blast_radius_score=0.5, gap_size=20
    )

    assert small_gap > large_gap
