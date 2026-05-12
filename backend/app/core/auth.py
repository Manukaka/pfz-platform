from dataclasses import dataclass
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import settings


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    role: str = "user"
    claims: dict[str, Any] | None = None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def _extract_role(claims: dict[str, Any]) -> str:
    metadata_sources = [
        claims,
        claims.get("app_metadata") or {},
        claims.get("user_metadata") or {},
    ]
    for source in metadata_sources:
        role = source.get("role")
        if role:
            return str(role)
        roles = source.get("roles")
        if isinstance(roles, list) and "admin" in roles:
            return "admin"
    return "user"


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_aud": False},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedUser(id=str(user_id), role=_extract_role(claims), claims=claims)


async def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
