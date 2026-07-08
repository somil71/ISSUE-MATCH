from collections.abc import Callable, Iterator
from dataclasses import dataclass

import tree_sitter_javascript as tsjs
import tree_sitter_python as tsp
import tree_sitter_typescript as tsts
from tree_sitter import Language, Node


def _child_text(node: Node, field: str, source: bytes) -> str | None:
    child = node.child_by_field_name(field)
    if child is None:
        return None
    return source[child.start_byte : child.end_byte].decode("utf-8", errors="replace")


def _text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _extract_reference_name(node: Node, source: bytes, dotted_field: str) -> str | None:
    """Resolves an identifier or a dotted access (attribute/member_expression)
    down to its rightmost segment, e.g. `foo.bar.baz` -> `baz`."""
    if node.type == "identifier":
        return _text(node, source)
    if node.type in ("attribute", "member_expression"):
        prop = node.child_by_field_name(dotted_field)
        if prop is not None:
            return _text(prop, source)
    return None


def _iter_python_functions(root: Node, source: bytes) -> Iterator[tuple[str, Node]]:
    def walk(node: Node) -> Iterator[tuple[str, Node]]:
        if node.type == "function_definition":
            name = _child_text(node, "name", source)
            if name:
                yield name, node
        for child in node.children:
            yield from walk(child)

    yield from walk(root)


def _iter_python_calls(root: Node, source: bytes) -> Iterator[str]:
    def walk(node: Node) -> Iterator[str]:
        if node.type == "call":
            fn = node.child_by_field_name("function")
            if fn is not None:
                name = _extract_reference_name(fn, source, "attribute")
                if name:
                    yield name
        for child in node.children:
            yield from walk(child)

    yield from walk(root)


_PYTHON_DECISION_TYPES = frozenset(
    {
        "if_statement",
        "elif_clause",
        "for_statement",
        "while_statement",
        "except_clause",
        "boolean_operator",
        "conditional_expression",
        "case_clause",
    }
)


def _python_is_decision(node: Node, source: bytes) -> bool:
    return node.type in _PYTHON_DECISION_TYPES


_JS_FUNCTION_DEF_TYPES = frozenset(
    {"function_declaration", "generator_function_declaration", "method_definition"}
)
_JS_FUNCTION_VALUE_TYPES = frozenset(
    {"arrow_function", "function_expression", "generator_function"}
)


def _iter_js_functions(root: Node, source: bytes) -> Iterator[tuple[str, Node]]:
    def walk(node: Node) -> Iterator[tuple[str, Node]]:
        if node.type in _JS_FUNCTION_DEF_TYPES:
            name = _child_text(node, "name", source)
            if name:
                yield name, node
        elif node.type == "variable_declarator":
            value = node.child_by_field_name("value")
            if value is not None and value.type in _JS_FUNCTION_VALUE_TYPES:
                name = _child_text(node, "name", source)
                if name:
                    yield name, value
        for child in node.children:
            yield from walk(child)

    yield from walk(root)


_JSX_ELEMENT_TYPES = frozenset({"jsx_opening_element", "jsx_self_closing_element"})


def _iter_js_calls(root: Node, source: bytes) -> Iterator[str]:
    """Yields names of both function calls and JSX component usages.

    Rendering a component via `<FitCard />` is a real dependency edge, just
    like calling a function — it is not a `call_expression` node in the JSX
    grammar, so it must be matched separately or every React/Next.js
    component would show zero fan-in regardless of how often it's used.
    """

    def walk(node: Node) -> Iterator[str]:
        if node.type == "call_expression":
            fn = node.child_by_field_name("function")
            if fn is not None:
                name = _extract_reference_name(fn, source, "property")
                if name:
                    yield name
        elif node.type in _JSX_ELEMENT_TYPES:
            tag = node.child_by_field_name("name")
            if tag is not None:
                name = _extract_reference_name(tag, source, "property")
                if name:
                    yield name
        for child in node.children:
            yield from walk(child)

    yield from walk(root)


_JS_DECISION_TYPES = frozenset(
    {
        "if_statement",
        "for_statement",
        "for_in_statement",
        "while_statement",
        "do_statement",
        "catch_clause",
        "ternary_expression",
        "switch_case",
    }
)
_JS_LOGICAL_OPERATORS = frozenset({"&&", "||", "??"})


def _js_is_decision(node: Node, source: bytes) -> bool:
    if node.type in _JS_DECISION_TYPES:
        return True
    if node.type == "binary_expression":
        operator = node.child_by_field_name("operator")
        if operator is not None:
            op_text = source[operator.start_byte : operator.end_byte].decode(
                "utf-8", errors="replace"
            )
            return op_text in _JS_LOGICAL_OPERATORS
    return False


@dataclass(frozen=True)
class LanguageSpec:
    key: str
    ts_language: Language
    extensions: frozenset[str]
    iter_functions: Callable[[Node, bytes], Iterator[tuple[str, Node]]]
    iter_calls: Callable[[Node, bytes], Iterator[str]]
    is_decision: Callable[[Node, bytes], bool]


LANGUAGES: dict[str, LanguageSpec] = {
    "python": LanguageSpec(
        key="python",
        ts_language=Language(tsp.language()),
        extensions=frozenset({".py"}),
        iter_functions=_iter_python_functions,
        iter_calls=_iter_python_calls,
        is_decision=_python_is_decision,
    ),
    "javascript": LanguageSpec(
        key="javascript",
        ts_language=Language(tsjs.language()),
        extensions=frozenset({".js", ".jsx", ".mjs", ".cjs"}),
        iter_functions=_iter_js_functions,
        iter_calls=_iter_js_calls,
        is_decision=_js_is_decision,
    ),
    "typescript": LanguageSpec(
        key="typescript",
        ts_language=Language(tsts.language_typescript()),
        extensions=frozenset({".ts"}),
        iter_functions=_iter_js_functions,
        iter_calls=_iter_js_calls,
        is_decision=_js_is_decision,
    ),
    "tsx": LanguageSpec(
        key="tsx",
        ts_language=Language(tsts.language_tsx()),
        extensions=frozenset({".tsx"}),
        iter_functions=_iter_js_functions,
        iter_calls=_iter_js_calls,
        is_decision=_js_is_decision,
    ),
}

_EXTENSION_TO_LANGUAGE: dict[str, LanguageSpec] = {
    ext: spec for spec in LANGUAGES.values() for ext in spec.extensions
}


def language_for_path(path: str) -> LanguageSpec | None:
    for ext, spec in _EXTENSION_TO_LANGUAGE.items():
        if path.endswith(ext):
            return spec
    return None
