from cryptography.fernet import Fernet
from itsdangerous import BadSignature, URLSafeTimedSerializer

from app.core.config import get_settings

SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 14


def _fernet() -> Fernet:
    return Fernet(get_settings().token_encryption_key.encode())


def encrypt_token(token: str) -> str:
    return _fernet().encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(get_settings().session_secret_key, salt="session")


def create_session_token(user_id: int) -> str:
    return _serializer().dumps({"user_id": user_id})


def read_session_token(token: str) -> int | None:
    try:
        data = _serializer().loads(token, max_age=SESSION_MAX_AGE_SECONDS)
    except BadSignature:
        return None
    return data.get("user_id")
