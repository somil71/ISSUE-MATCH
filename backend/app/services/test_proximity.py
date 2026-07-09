import re
from collections import Counter
from pathlib import PurePosixPath

from app.services.parsing.engine import ParsedFile

_PYTHON_TEST_FILE = re.compile(r"(^|/)(test_[^/]+\.py|[^/]+_test\.py)$")
_JS_TEST_FILE = re.compile(r"\.(test|spec)\.[jt]sx?$")
_TEST_DIR_SEGMENTS = frozenset({"test", "tests", "__tests__", "spec", "specs"})


def is_test_file(relative_path: str) -> bool:
    posix_path = relative_path.replace("\\", "/")
    if _PYTHON_TEST_FILE.search(posix_path):
        return True
    if _JS_TEST_FILE.search(posix_path):
        return True
    parts = PurePosixPath(posix_path).parts
    return any(part.lower() in _TEST_DIR_SEGMENTS for part in parts[:-1])


def build_tested_names(parsed_files: list[ParsedFile]) -> frozenset[str]:
    """Names referenced (called, or used as a JSX component) from any file
    recognized as a test file, repo-wide. Like fan-in, this is name-based,
    not a true coverage tool: it doesn't verify the test actually exercises
    the right code path, only that it references the function by name.
    """
    tested: set[str] = set()
    for parsed_file in parsed_files:
        if is_test_file(parsed_file.relative_path):
            tested.update(parsed_file.call_names)
    return frozenset(tested)


def find_test_directory_convention(parsed_files: list[ParsedFile]) -> str | None:
    """The most common directory holding test files in this repo, so "add a
    test" guidance can point at a real, existing convention instead of
    inventing one. None if the repo has no recognized test files at all."""
    directory_counts: Counter[str] = Counter()
    for parsed_file in parsed_files:
        posix_path = parsed_file.relative_path.replace("\\", "/")
        if not is_test_file(posix_path):
            continue
        directory_counts["." if "/" not in posix_path else posix_path.rsplit("/", 1)[0]] += 1

    if not directory_counts:
        return None
    return directory_counts.most_common(1)[0][0]
