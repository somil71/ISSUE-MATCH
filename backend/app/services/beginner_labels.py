import re

_BEGINNER_LABEL_PATTERNS = (
    re.compile(r"good[\s-]*first[\s-]*issue", re.IGNORECASE),
    re.compile(r"beginner[\s-]*friendly", re.IGNORECASE),
    re.compile(r"help[\s-]*wanted", re.IGNORECASE),
    re.compile(r"^easy$", re.IGNORECASE),
    re.compile(r"^starter$", re.IGNORECASE),
    re.compile(r"up[\s-]*for[\s-]*grabs", re.IGNORECASE),
    re.compile(r"first[\s-]*timers?[\s-]*only", re.IGNORECASE),
)


def is_beginner_friendly_label(label_name: str) -> bool:
    return any(pattern.search(label_name) for pattern in _BEGINNER_LABEL_PATTERNS)


def has_beginner_friendly_label(label_names: list[str]) -> bool:
    return any(is_beginner_friendly_label(name) for name in label_names)
