from collections import Counter, defaultdict
from dataclasses import dataclass

from app.services.parsing.engine import ParsedFile, ParsedFunction


@dataclass
class FunctionMetrics:
    function: ParsedFunction
    fan_in: int
    name_is_ambiguous: bool


def build_fan_in(parsed_files: list[ParsedFile]) -> dict[str, FunctionMetrics]:
    """Resolves call sites to function definitions by name, repo-wide.

    This is name-based resolution, not full scope/type analysis: a call to
    `foo()` is credited to the single repo-wide definition of `foo`. When more
    than one function shares a name, the match is ambiguous and is not
    credited to any of them (silently guessing which one was meant would
    violate the product's "every number is traceable" guarantee) — those
    functions are flagged via `name_is_ambiguous` instead.
    """
    functions_by_name: dict[str, list[ParsedFunction]] = defaultdict(list)
    all_functions: dict[str, ParsedFunction] = {}
    for parsed_file in parsed_files:
        for fn in parsed_file.functions:
            functions_by_name[fn.name].append(fn)
            all_functions[fn.id] = fn

    call_counts: Counter[str] = Counter()
    for parsed_file in parsed_files:
        call_counts.update(parsed_file.call_names)

    fan_in_by_id: dict[str, int] = dict.fromkeys(all_functions, 0)
    ambiguous_names: set[str] = set()

    for name, count in call_counts.items():
        candidates = functions_by_name.get(name)
        if not candidates:
            continue
        if len(candidates) == 1:
            fan_in_by_id[candidates[0].id] += count
        else:
            ambiguous_names.add(name)

    return {
        fid: FunctionMetrics(
            function=fn,
            fan_in=fan_in_by_id[fid],
            name_is_ambiguous=fn.name in ambiguous_names,
        )
        for fid, fn in all_functions.items()
    }
