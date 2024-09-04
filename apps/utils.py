from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError

from models import User


SECRET_KEY = 'thisismysecretkey'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(password: str, hashed_password: str):
    return bcrypt_context.verify(password, hashed_password)


def hash_password(password: str):
    return bcrypt_context.hash(password)


def authenticate_user(db, username: str, password: str):
    user = User.get_user_by_username(username, db)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt