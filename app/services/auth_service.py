# ============================================================
# app/services/auth_service.py — Authentication Business Logic
#
# Laravel equivalent: a combination of:
#   - Hash facade (Hash::make, Hash::check)
#   - tymon/jwt-auth JWTAuth facade
#   - AuthController logic
#
# This file handles:
#   1. Password hashing & verification
#   2. JWT token creation
#   3. JWT token decoding/validation
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.schemas.user import TokenData


# -------------------------------------------------------
# Password Hashing Context
#
# Laravel equivalent:
#   Hash::make($password)   → pwd_context.hash(password)
#   Hash::check($p, $hash)  → pwd_context.verify(plain, hashed)
#
# bcrypt is the same algorithm Laravel uses by default.
# CryptContext manages the algorithm and can handle upgrades
# (e.g., if you switch from md5 to bcrypt, old hashes still work).
# -------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.

    Laravel: Hash::make($password)
    Python:  hash_password(password)

    Returns a bcrypt hash string like:
    "$2b$12$abc123..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check a plain-text password against a bcrypt hash.

    Laravel: Hash::check($plainText, $hashedPassword)
    Python:  verify_password(plain, hashed)

    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------------------------------
# JWT Token Creation
#
# Laravel equivalent: JWTAuth::fromUser($user) from tymon/jwt-auth
#
# A JWT has three parts: header.payload.signature
# The payload contains claims like user_id and expiration time.
# The signature uses our SECRET_KEY to prevent tampering.
# -------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT token.

    Laravel: JWTAuth::fromUser($user)
    Python:  create_access_token({"sub": str(user.id)})

    Args:
        data: dict of claims to encode (e.g., {"sub": "123"})
        expires_delta: how long until the token expires

    Returns:
        A signed JWT string like "eyJ0eXAiOiJKV1QiLCJhbGci..."
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    # "exp" is a standard JWT claim for expiration time
    to_encode.update({"exp": expire})

    # Encode the payload into a signed JWT string
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


# -------------------------------------------------------
# JWT Token Decoding
#
# Laravel equivalent: JWTAuth::parseToken()->authenticate()
# -------------------------------------------------------
def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.

    Raises ValueError if the token is invalid or expired.
    The caller (dependencies.py) converts this to an HTTPException(401).

    Args:
        token: the raw JWT string from the Authorization header

    Returns:
        TokenData with the user_id extracted from the payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        # "sub" (subject) is the standard JWT claim we use to store user ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Token missing 'sub' claim")

        return TokenData(user_id=int(user_id))

    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
