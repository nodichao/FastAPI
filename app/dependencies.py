
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from app.database import get_db
from app.models import UserModel
from app.security import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()

def get_current_user(
    bearer_sheme: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            bearer_sheme.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user = db.get(UserModel, user_id)

    if user is None:
        raise credentials_exception

    return user
