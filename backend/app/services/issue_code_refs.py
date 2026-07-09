import re

_BACKTICK_SPAN = re.compile(r"`([^`\n]{1,120})`")


def extract_backtick_references(text: str) -> list[str]:
    return [match.group(1).strip() for match in _BACKTICK_SPAN.finditer(text)]


def match_code_references(
    references: list[str], cached_functions: dict[str, list[dict]], cached_files: list[str]
) -> list[dict]:
    """Resolves explicit backtick-quoted mentions in issue text (function
    names or file paths) against the cached blast-radius analysis. Only
    exact function names or file-path suffix matches count -- no fuzzy
    matching -- so every reference shown is something the issue author
    genuinely named, not a guess.
    """
    matched: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for raw_ref in references:
        ref = raw_ref.strip().strip("()[]{}").split("(")[0].strip()
        if not ref:
            continue

        if ref in cached_functions:
            for entry in cached_functions[ref]:
                key = (ref, entry["file"])
                if key in seen:
                    continue
                seen.add(key)
                matched.append(
                    {
                        "name": ref,
                        "file": entry["file"],
                        "bucket": entry["bucket"],
                        "summary": entry.get("summary"),
                    }
                )
            continue

        for file_path in cached_files:
            if file_path == ref or file_path.endswith("/" + ref):
                key = ("__file__", file_path)
                if key in seen:
                    continue
                seen.add(key)
                matched.append(
                    {
                        "name": None,
                        "file": file_path,
                        "bucket": _worst_bucket_in_file(file_path, cached_functions),
                        "summary": None,
                    }
                )

    return matched


def _worst_bucket_in_file(file_path: str, cached_functions: dict[str, list[dict]]) -> str | None:
    buckets = {
        entry["bucket"]
        for entries in cached_functions.values()
        for entry in entries
        if entry["file"] == file_path
    }
    if "here_be_dragons" in buckets:
        return "here_be_dragons"
    if "start_here" in buckets:
        return "start_here"
    return None
