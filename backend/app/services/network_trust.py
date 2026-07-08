from collections import Counter
from datetime import UTC, datetime

_MAX_RECORDED = 500
_calls: list[dict] = []


def record_call(host: str | None) -> None:
    """Every outbound HTTP call the whole backend makes is routed through
    here (see github_client._request) -- this is what lets the trust panel
    show the real, live list of external hosts contacted, rather than just
    asserting "no LLM calls happen" in prose."""
    _calls.append({"host": host or "unknown", "at": datetime.now(UTC).isoformat()})
    if len(_calls) > _MAX_RECORDED:
        del _calls[: len(_calls) - _MAX_RECORDED]


def summary() -> dict:
    hosts = Counter(c["host"] for c in _calls)
    return {
        "total_calls": len(_calls),
        "hosts": [{"host": host, "count": count} for host, count in hosts.most_common()],
        "since": _calls[0]["at"] if _calls else None,
    }
