from app.services.beginner_labels import has_beginner_friendly_label, is_beginner_friendly_label


def test_recognizes_common_beginner_label_spellings() -> None:
    assert is_beginner_friendly_label("good first issue")
    assert is_beginner_friendly_label("good-first-issue")
    assert is_beginner_friendly_label("Good First Issue")
    assert is_beginner_friendly_label("help wanted")
    assert is_beginner_friendly_label("help-wanted")
    assert is_beginner_friendly_label("beginner-friendly")
    assert is_beginner_friendly_label("easy")
    assert is_beginner_friendly_label("up-for-grabs")


def test_rejects_unrelated_labels() -> None:
    assert not is_beginner_friendly_label("enhancement")
    assert not is_beginner_friendly_label("bug")
    assert not is_beginner_friendly_label("wontfix")
    assert not is_beginner_friendly_label("easypeasy")


def test_has_beginner_friendly_label_checks_whole_list() -> None:
    assert has_beginner_friendly_label(["enhancement", "good first issue"])
    assert not has_beginner_friendly_label(["enhancement", "bug"])
