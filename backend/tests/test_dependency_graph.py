from pathlib import Path

from app.services.dependency_graph import (
    build_call_graph,
    transitive_dependencies,
    transitive_dependents,
)
from app.services.parsing.engine import parse_file


def test_call_edges_attribute_to_precise_enclosing_function(tmp_path: Path) -> None:
    source = """
def leaf():
    return 1

def middle():
    return leaf()

def top():
    return middle()
"""
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    graph = build_call_graph([parsed])
    by_name = {fn.name: fn.id for fn in graph.all_functions.values()}

    assert graph.edges[by_name["top"]] == {by_name["middle"]}
    assert graph.edges[by_name["middle"]] == {by_name["leaf"]}
    assert by_name["leaf"] not in graph.edges


def test_module_level_calls_have_no_caller_edge(tmp_path: Path) -> None:
    source = """
def helper():
    return 1

helper()
"""
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    graph = build_call_graph([parsed])
    assert graph.edges == {}


def test_transitive_dependents_walks_multiple_hops(tmp_path: Path) -> None:
    source = """
def leaf():
    return 1

def middle():
    return leaf()

def top():
    return middle()

def unrelated():
    return 2
"""
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    graph = build_call_graph([parsed])
    by_name = {fn.name: fn.id for fn in graph.all_functions.values()}

    dependents = transitive_dependents(by_name["leaf"], graph, max_hops=4)
    assert dependents == {by_name["middle"]: 1, by_name["top"]: 2}
    assert by_name["unrelated"] not in dependents


def test_transitive_dependents_respects_max_hops(tmp_path: Path) -> None:
    source = """
def leaf():
    return 1

def middle():
    return leaf()

def top():
    return middle()
"""
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    graph = build_call_graph([parsed])
    by_name = {fn.name: fn.id for fn in graph.all_functions.values()}

    dependents = transitive_dependents(by_name["leaf"], graph, max_hops=1)
    assert dependents == {by_name["middle"]: 1}


def test_transitive_dependencies_walks_the_forward_graph(tmp_path: Path) -> None:
    source = """
def leaf():
    return 1

def middle():
    return leaf()

def top():
    return middle()
"""
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    graph = build_call_graph([parsed])
    by_name = {fn.name: fn.id for fn in graph.all_functions.values()}

    dependencies = transitive_dependencies(by_name["top"], graph, max_hops=4)
    assert dependencies == {by_name["middle"]: 1, by_name["leaf"]: 2}


def test_ambiguous_callee_names_are_not_wired_into_edges(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("def process():\n    return 1\n")
    (tmp_path / "b.py").write_text("def process():\n    return 2\n")
    (tmp_path / "c.py").write_text("def caller():\n    process()\n")

    parsed_files = []
    for filename in ("a.py", "b.py", "c.py"):
        parsed = parse_file(tmp_path / filename, filename)
        assert parsed is not None
        parsed_files.append(parsed)

    graph = build_call_graph(parsed_files)
    by_name = {fn.name: fn.id for fn in graph.all_functions.values()}

    assert graph.edges.get(by_name["caller"], set()) == set()


def test_recursive_calls_are_not_self_loops(tmp_path: Path) -> None:
    source = """
def countdown(n):
    if n <= 0:
        return 0
    return countdown(n - 1)
"""
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    graph = build_call_graph([parsed])
    by_name = {fn.name: fn.id for fn in graph.all_functions.values()}

    assert graph.edges.get(by_name["countdown"], set()) == set()


def test_jsx_component_usage_creates_a_real_edge(tmp_path: Path) -> None:
    source = """
function FitCard() {
  return <div>card</div>;
}

function FitGrid() {
  return (
    <div>
      <FitCard />
    </div>
  );
}
"""
    path = tmp_path / "sample.tsx"
    path.write_text(source)
    parsed = parse_file(path, "sample.tsx")
    assert parsed is not None

    graph = build_call_graph([parsed])
    by_name = {fn.name: fn.id for fn in graph.all_functions.values()}

    assert graph.edges[by_name["FitGrid"]] == {by_name["FitCard"]}
    dependents = transitive_dependents(by_name["FitCard"], graph)
    assert dependents == {by_name["FitGrid"]: 1}
