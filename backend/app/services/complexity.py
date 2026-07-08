from tree_sitter import Node

from app.services.parsing.languages import LanguageSpec


def cyclomatic_complexity(function_node: Node, source: bytes, language: LanguageSpec) -> int:
    complexity = 1

    def walk(node: Node) -> None:
        nonlocal complexity
        if language.is_decision(node, source):
            complexity += 1
        for child in node.children:
            walk(child)

    walk(function_node)
    return complexity
