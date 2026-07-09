def draft_intro_comment(
    reference: dict | None,
    owner: dict | None,
    user_skills: list[str],
) -> str:
    """Composes a real, copy-pasteable "I'd like to work on this" GitHub
    comment -- not a report about the issue, an artifact the contributor
    actually posts. Built entirely from data already computed elsewhere
    (the blast radius summary sentence, real git commit authorship, the
    user's own skill profile), never a model -- any piece that's missing
    is simply left out rather than guessed at.
    """
    greeting = f"Hi @{owner['author']}," if owner else "Hi,"
    sentences = [f"{greeting} I'd like to work on this issue."]

    if reference is not None and reference.get("summary"):
        target = f"`{reference['name']}`" if reference.get("name") else f"`{reference['file']}`"
        location = f" in `{reference['file']}`" if reference.get("name") else ""
        clause = reference["summary"].rstrip(".").lower()
        sentences.append(f"Looking at {target}{location}: {clause}.")

    if user_skills:
        sentences.append(f"I've got experience with {', '.join(user_skills)}.")

    sentences.append("Let me know if there's a preferred approach before I dive in!")
    return " ".join(sentences)
