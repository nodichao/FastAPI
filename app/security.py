from pwdlib import PasswordHash
import os
import jwt
import datetime
from datetime import timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user_id: str) -> str:
    expires_at = datetime.datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# hashed_password = hash_password("MonMotDePasse123")

# print(verify_password("MonMotDePasse123", hashed_password))  # Devrait retourner True
# print(verify_password("MotDePasseIncorrect", hashed_password))  # Devrait retourner False