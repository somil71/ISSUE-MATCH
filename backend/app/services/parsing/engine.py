from dataclasses import dataclass
from pathlib import Path

from tree_sitter import Node, Parser, Tree

from app.services.parsing.languages import LanguageSpec, language_for_path


@dataclass
class ParsedFunction:
    id: str
    name: str
    relative_path: str
    start_line: int
    end_line: int
    node: Node
    source: bytes
    language: LanguageSpec


@dataclass
class ParsedFile:
    relative_path: str
    language: LanguageSpec
    source: bytes
    tree: Tree
    functions: list[ParsedFunction]
    call_names: list[str]


def parse_file(path: Path, relative_path: str) -> ParsedFile | None:
    language = language_for_path(relative_path)
    if language is None:
        return None

    source = path.read_bytes()
    parser = Parser(language.ts_language)
    tree = parser.parse(source)
    root = tree.root_node

    functions = [
        ParsedFunction(
            id=f"{relative_path}::{name}:{node.start_point[0] + 1}",
            name=name,
            relative_path=relative_path,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            node=node,
            source=source,
            language=language,
        )
        for name, node in language.iter_functions(root, source)
    ]
    call_names = list(language.iter_calls(root, source))

    return ParsedFile(
        relative_path=relative_path,
        language=language,
        source=source,
        tree=tree,
        functions=functions,
        call_names=call_names,
    )
