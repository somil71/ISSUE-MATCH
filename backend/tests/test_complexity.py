from pathlib import Path

from app.services.complexity import cyclomatic_complexity
from app.services.parsing.engine import parse_file


def _functions(tmp_path: Path, filename: str, source: str) -> dict[str, int]:
    path = tmp_path / filename
    path.write_text(source)
    parsed = parse_file(path, filename)
    assert parsed is not None
    return {
        fn.name: cyclomatic_complexity(fn.node, fn.source, fn.language)
        for fn in parsed.functions
    }


def test_python_complexity(tmp_path: Path) -> None:
    source = """
def simple():
    return 1

def with_if(x):
    if x:
        return 1
    return 0

def with_if_elif_else(x):
    if x == 1:
        return 1
    elif x == 2:
        return 2
    else:
        return 3

def with_bool(x, y):
    if x and y:
        return 1
    return 0
"""
    complexities = _functions(tmp_path, "sample.py", source)

    assert complexities["simple"] == 1
    assert complexities["with_if"] == 2
    assert complexities["with_if_elif_else"] == 3
    assert complexities["with_bool"] == 3


def test_javascript_complexity(tmp_path: Path) -> None:
    source = """
function greet(name) {
  return name ? `hi ${name}` : "hi";
}

const helper = (a, b) => {
  if (a && b) {
    return a;
  }
  return b;
};

function caller() {
  return 1;
}
"""
    complexities = _functions(tmp_path, "sample.js", source)

    assert complexities["greet"] == 2
    assert complexities["helper"] == 3
    assert complexities["caller"] == 1
