import hashlib
import secrets

def get_key_hash(plain_key: str) -> str:
    """
    Returns SHA256 hash of the key.
    We use SHA256 because we need a deterministic hash to look up
    users by API key in the database (WHERE api_key_hash = ...).
    """
    return hashlib.sha256(plain_key.encode()).hexdigest()

def verify_key(plain_key: str, hashed_key: str) -> bool:
    return get_key_hash(plain_key) == hashed_key

def generate_api_key() -> str:
    return secrets.token_urlsafe(32)
