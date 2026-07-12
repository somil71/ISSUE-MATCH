from dataclasses import dataclass

from app.services.embeddings import embed_texts


@dataclass
class IssueMatch:
    issue_index: int
    similarity: float
    overlapping_terms: list[str]


def rank_issues(
    user_skill_text: str, issue_texts: list[str], top_terms: int = 5
) -> list[IssueMatch]:
    if not issue_texts:
        return []

    embeddings = embed_texts([user_skill_text, *issue_texts])
    user_vector = embeddings[0]
    issue_vectors = embeddings[1:]

    similarities = issue_vectors @ user_vector
    overlaps = _tfidf_overlap(user_skill_text, issue_texts, top_terms)

    matches = [
        IssueMatch(
            issue_index=i,
            similarity=float(similarities[i]),
            overlapping_terms=overlaps[i],
        )
        for i in range(len(issue_texts))
    ]
    matches.sort(key=lambda m: m.similarity, reverse=True)
    return matches


def _tfidf_overlap(
    user_text: str, issue_texts: list[str], top_terms: int
) -> list[list[str]]:
    """For each issue, the terms that appear in both the issue text and the
    user's skill text, ranked by the issue's own TF-IDF weight for that term
    — this is what actually gets shown as "why this matched", not the bare
    similarity float.
    """
    # Imported here, not at module load -- see embeddings.py for why.
    from sklearn.feature_extraction.text import TfidfVectorizer

    documents = [user_text, *issue_texts]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
    matrix = vectorizer.fit_transform(documents)
    vocabulary = vectorizer.get_feature_names_out()

    user_terms = set(vocabulary[matrix[0].nonzero()[1]])

    overlaps: list[list[str]] = []
    for i in range(1, len(documents)):
        row = matrix[i]
        scored = {
            vocabulary[idx]: row[0, idx]
            for idx in row.nonzero()[1]
            if vocabulary[idx] in user_terms
        }
        top = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)[:top_terms]
        overlaps.append([term for term, _ in top])
    return overlaps
