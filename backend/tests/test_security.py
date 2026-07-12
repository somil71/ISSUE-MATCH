from app.core.security import (
    create_session_token,
    decrypt_token,
    encrypt_token,
    read_session_token,
)


def test_encrypt_decrypt_token_round_trips() -> None:
    original = "gho_realGitHubAccessTokenLookingString123"
    encrypted = encrypt_token(original)

    assert encrypted != original
    assert decrypt_token(encrypted) == original


def test_encrypted_token_is_not_plaintext_recoverable_without_decrypt() -> None:
    encrypted = encrypt_token("super-secret-value")
    assert "super-secret-value" not in encrypted


def test_session_token_round_trips_the_user_id() -> None:
    token = create_session_token(42)
    assert read_session_token(token) == 42


def test_session_token_rejects_a_tampered_signature() -> None:
    token = create_session_token(7)
    parts = token.split(".")
    sig = parts[2]
    sig_mutated = sig[:5] + ("x" if sig[5] != "x" else "y") + sig[6:]
    parts[2] = sig_mutated
    tampered = ".".join(parts)

    assert read_session_token(tampered) is None


def test_session_token_rejects_garbage_input() -> None:
    assert read_session_token("not-a-real-token") is None
