from app.services.issue_code_refs import extract_backtick_references, match_code_references


def test_extract_backtick_references_finds_all_spans() -> None:
    text = "Fix `parseConfig` in `lib/config.ts`, also check `helper`."
    assert extract_backtick_references(text) == ["parseConfig", "lib/config.ts", "helper"]


def test_extract_backtick_references_ignores_unquoted_text() -> None:
    text = "No backticks here, just prose about parseConfig."
    assert extract_backtick_references(text) == []


def test_match_code_references_resolves_function_name() -> None:
    cached_functions = {
        "parseConfig": [{"file": "lib/config.ts", "bucket": "here_be_dragons", "score": 0.7}],
    }
    matched = match_code_references(["parseConfig"], cached_functions, [])
    assert matched == [
        {"name": "parseConfig", "file": "lib/config.ts", "bucket": "here_be_dragons"}
    ]


def test_match_code_references_resolves_file_path_to_worst_bucket() -> None:
    cached_functions = {
        "a": [{"file": "lib/config.ts", "bucket": "start_here", "score": 0.1}],
        "b": [{"file": "lib/config.ts", "bucket": "here_be_dragons", "score": 0.8}],
    }
    matched = match_code_references(["lib/config.ts"], cached_functions, ["lib/config.ts"])
    assert matched == [{"name": None, "file": "lib/config.ts", "bucket": "here_be_dragons"}]


def test_match_code_references_ignores_unmatched_references() -> None:
    matched = match_code_references(["somethingNotInTheRepo"], {}, ["lib/config.ts"])
    assert matched == []


def test_match_code_references_deduplicates() -> None:
    cached_functions = {
        "parseConfig": [{"file": "lib/config.ts", "bucket": "start_here", "score": 0.1}],
    }
    matched = match_code_references(["parseConfig", "parseConfig"], cached_functions, [])
    assert len(matched) == 1
