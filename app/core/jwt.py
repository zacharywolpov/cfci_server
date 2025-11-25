from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import get_settings

settings = get_settings()

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: int = 120) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None