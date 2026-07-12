import re
from functools import lru_cache

MODEL_NAME = "en_core_web_sm"

_IMPERATIVE_VERBS = frozenset(
    {
        "add", "fix", "update", "refactor", "remove", "improve", "implement",
        "support", "handle", "allow", "prevent", "migrate", "deprecate",
        "upgrade", "downgrade", "rename", "move", "optimize", "clean",
        "simplify", "replace", "revert", "enable", "disable", "validate",
        "sanitize", "document", "investigate", "resolve", "correct",
    }
)

# Longer phrases are checked before their component words, so multi-word
# terms win (e.g. "oauth token refresh" is replaced whole, not word-by-word).
_GLOSSARY = {
    "oauth token refresh": "keeping you logged in without re-entering your password",
    "race condition": "a bug caused by timing between simultaneous operations",
    "null pointer": "a bug from using something that doesn't exist yet",
    "authentication": "logging in",
    "middleware": "a step that runs before your request is handled",
    "endpoint": "a URL the app responds to",
    "migration": "a change to the database's structure",
    "schema": "the database's structure",
    "webhook": "an automatic notification sent to another service",
    "regression": "something that used to work but broke",
    "serialize": "convert into a saveable/sendable format",
    "sanitize": "clean unsafe input",
    "validate": "check for correctness",
    "cache": "temporary storage for faster access",
    "async": "non-blocking",
    "token": "a temporary access key",
    "deprecate": "phase out",
}

_ARTICLE_STARTERS = ("a ", "an ", "the ", "your ", "my ", "our ")

# Real GitHub issues overwhelmingly use conventional-commit or "Feature
# Request:"/"Bug:" prefixes rather than a bare imperative sentence -- without
# stripping these first, the first-word verb check almost never fires and
# every title falls through to the low-value fallback. "bug"/"fix" prefixes
# also pick the "problem" framing below instead of the neutral one.
_PREFIX_PATTERN = re.compile(
    r"^(feat|feature request|feature|fix|bug report|bug|chore|docs|"
    r"refactor|test|perf|style|enhancement)(\([^)]*\))?\s*:\s*",
    re.IGNORECASE,
)
_PROBLEM_PREFIXES = frozenset({"fix", "bug", "bug report"})


def _strip_prefix(title: str) -> tuple[str, str | None]:
    match = _PREFIX_PATTERN.match(title)
    if not match:
        return title, None
    return title[match.end() :].strip(), match.group(1).lower()


@lru_cache
def _model():
    # Imported here, not at module load -- see embeddings.py for why.
    import spacy

    return spacy.load(MODEL_NAME)


def _gerund(verb: str) -> str:
    if verb.endswith("e") and not verb.endswith("ee"):
        return verb[:-1] + "ing"
    return verb + "ing"


def _with_article(phrase: str) -> str:
    if phrase.lower().startswith(_ARTICLE_STARTERS):
        return phrase
    return "the " + phrase


def _simplify_phrase(phrase: str) -> str:
    """Whole-word/phrase substitution only — a naive substring match would
    corrupt inflected forms, e.g. "deprecate" matching inside "deprecated"
    or "endpoint" matching inside "endpoints"."""
    result = phrase
    for term, plain in sorted(_GLOSSARY.items(), key=lambda kv: -len(kv[0])):
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        result = pattern.sub(plain, result)
    return result


def explain_issue(title: str) -> str:
    """Deterministic template, no LLM. Imperative titles ("Add X") are
    checked against a fixed verb list first since spaCy's small model
    mistags them on short title-case text; bug-report titles with no clear
    verb fall back to describing the whole title rather than fabricating a
    verb-object structure that isn't there."""
    cleaned, prefix_kind = _strip_prefix(title.strip())
    is_problem = prefix_kind in _PROBLEM_PREFIXES
    fallback_verb = "describes a problem involving" if is_problem else "is about"

    doc = _model()(cleaned)
    if len(doc) == 0:
        return "No description available."

    first_word = doc[0].text.lower()
    root = next((t for t in doc if t.dep_ == "ROOT"), doc[0])

    if first_word in _IMPERATIVE_VERBS:
        remainder = doc[1:].text.strip()
        component = _with_article(_simplify_phrase(remainder)) if remainder else "the codebase"
        return f"This issue is about {_gerund(first_word)} {component}."

    if root.pos_ == "VERB":
        dobj = next((c for c in root.children if c.dep_ in ("dobj", "attr")), None)
        if dobj is not None:
            component = doc[dobj.left_edge.i : dobj.right_edge.i + 1].text
            return f"This issue is about {_gerund(root.lemma_)} {_with_article(_simplify_phrase(component))}."

    subject_span = doc[root.left_edge.i : root.right_edge.i + 1].text
    return f"This issue {fallback_verb} {_with_article(_simplify_phrase(subject_span))}."
