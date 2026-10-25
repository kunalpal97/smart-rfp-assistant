
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.core.security import AuthenticatedUser


def require_user(
    current_user: Annotated[
        AuthenticatedUser,
        Depends(get_current_user),
    ],
) -> AuthenticatedUser:
    """Allow users assigned either User or Admin role."""

    if not {"User", "Admin"}.intersection(current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User or Admin role required.",
        )

    return current_user


def require_admin(
    current_user: Annotated[
        AuthenticatedUser,
        Depends(get_current_user),
    ],
) -> AuthenticatedUser:
    """Allow only users assigned the Admin role."""

    if "Admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required.",
        )

    return current_user
