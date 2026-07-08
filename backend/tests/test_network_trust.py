from app.services import network_trust


def test_summary_counts_calls_by_host() -> None:
    network_trust._calls.clear()
    network_trust.record_call("api.github.com")
    network_trust.record_call("api.github.com")
    network_trust.record_call("github.com")

    result = network_trust.summary()

    assert result["total_calls"] == 3
    assert result["hosts"] == [
        {"host": "api.github.com", "count": 2},
        {"host": "github.com", "count": 1},
    ]
    assert result["since"] is not None


def test_summary_caps_recorded_history() -> None:
    network_trust._calls.clear()
    for _ in range(network_trust._MAX_RECORDED + 50):
        network_trust.record_call("api.github.com")

    assert len(network_trust._calls) == network_trust._MAX_RECORDED
