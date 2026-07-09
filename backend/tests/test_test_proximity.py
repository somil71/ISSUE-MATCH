from pathlib import Path

from app.services.parsing.engine import parse_file
from app.services.test_proximity import (
    build_tested_names,
    find_test_directory_convention,
    is_test_file,
)


def test_is_test_file_recognizes_common_conventions() -> None:
    assert is_test_file("tests/test_auth.py")
    assert is_test_file("auth_test.py")
    assert is_test_file("src/components/Button.test.tsx")
    assert is_test_file("src/components/Button.spec.ts")
    assert is_test_file("src/__tests__/Button.tsx")
    assert not is_test_file("src/components/Button.tsx")
    assert not is_test_file("app/testing_utils.py")


def test_build_tested_names_only_credits_functions_called_from_test_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text(
        "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n"
    )
    (tmp_path / "test_app.py").write_text("from app import add\n\ndef test_add():\n    add(1, 2)\n")

    parsed_files = []
    for name in ("app.py", "test_app.py"):
        parsed = parse_file(tmp_path / name, name)
        assert parsed is not None
        parsed_files.append(parsed)

    tested = build_tested_names(parsed_files)

    assert "add" in tested
    assert "subtract" not in tested


def test_find_test_directory_convention_picks_most_common_dir(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("def add():\n    return 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("def test_a():\n    pass\n")
    (tmp_path / "tests" / "test_b.py").write_text("def test_b():\n    pass\n")

    parsed_files = []
    for relative in ("app.py", "tests/test_a.py", "tests/test_b.py"):
        parsed = parse_file(tmp_path / relative, relative)
        assert parsed is not None
        parsed_files.append(parsed)

    assert find_test_directory_convention(parsed_files) == "tests"


def test_find_test_directory_convention_returns_none_without_test_files(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("def add():\n    return 1\n")
    parsed = parse_file(tmp_path / "app.py", "app.py")
    assert parsed is not None

    assert find_test_directory_convention([parsed]) is None
