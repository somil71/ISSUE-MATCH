from pathlib import Path

from app.services.call_graph import build_fan_in
from app.services.parsing.engine import parse_file


def test_fan_in_counts_calls_by_name(tmp_path: Path) -> None:
    source = """
function greet(name) {
  return name;
}

const helper = (a, b) => {
  return a + b;
};

function caller() {
  greet("x");
  greet("y");
  helper(1, 2);
}
"""
    path = tmp_path / "sample.js"
    path.write_text(source)
    parsed = parse_file(path, "sample.js")
    assert parsed is not None

    metrics = build_fan_in([parsed])
    by_name = {fm.function.name: fm for fm in metrics.values()}

    assert by_name["greet"].fan_in == 2
    assert by_name["helper"].fan_in == 1
    assert by_name["caller"].fan_in == 0
    assert not by_name["greet"].name_is_ambiguous


def test_fan_in_counts_jsx_component_usage(tmp_path: Path) -> None:
    source = """
function FitCard() {
  return <div>card</div>;
}

function FitGrid() {
  return (
    <div>
      <FitCard />
      <FitCard key="a" />
    </div>
  );
}
"""
    path = tmp_path / "sample.tsx"
    path.write_text(source)
    parsed = parse_file(path, "sample.tsx")
    assert parsed is not None

    metrics = build_fan_in([parsed])
    by_name = {fm.function.name: fm for fm in metrics.values()}

    assert by_name["FitCard"].fan_in == 2
    assert by_name["FitGrid"].fan_in == 0


def test_fan_in_flags_ambiguous_names_instead_of_guessing(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("def process():\n    return 1\n")
    (tmp_path / "b.py").write_text("def process():\n    return 2\n")
    (tmp_path / "c.py").write_text("def caller():\n    process()\n")

    parsed_files = []
    for name in ("a.py", "b.py", "c.py"):
        parsed = parse_file(tmp_path / name, name)
        assert parsed is not None
        parsed_files.append(parsed)

    metrics = build_fan_in(parsed_files)
    process_defs = [fm for fm in metrics.values() if fm.function.name == "process"]

    assert len(process_defs) == 2
    assert all(fm.name_is_ambiguous for fm in process_defs)
    assert all(fm.fan_in == 0 for fm in process_defs)
