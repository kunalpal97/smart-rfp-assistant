
from dataclasses import dataclass
from functools import lru_cache

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

from app.core.config import get_settings


class TokenValidationError(Exception):
    """Raised when an access token fails authentication."""


@dataclass(frozen=True)
class AuthenticatedUser:
    tenant_id: str
    object_id: str
    roles: tuple[str, ...]
    scopes: tuple[str, ...]


@lru_cache(maxsize=1)
def get_jwks_client() -> PyJWKClient:
    """Reuse Microsoft's public signing-key client."""

    settings = get_settings()

    jwks_url = (
        "https://login.microsoftonline.com/"
        f"{settings.entra_tenant_id}/discovery/v2.0/keys"
    )

    return PyJWKClient(
        jwks_url,
        cache_jwk_set=True,
        lifespan=3600,
        timeout=5,
    )


def validate_access_token(token: str) -> AuthenticatedUser:
    """
    Verify a Microsoft Entra v2 delegated access token.

    Returns a trusted identity only after all checks pass.
    """

    settings = get_settings()

    if not all((
        settings.entra_tenant_id,
        settings.entra_client_id,
        settings.entra_api_audience,
        settings.entra_required_scope,
    )):
        raise RuntimeError(
            "Microsoft Entra authentication is not configured."
        )

    issuer = (
        "https://login.microsoftonline.com/"
        f"{settings.entra_tenant_id}/v2.0"
    )

    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(
            token
        )

        claims = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=["RS256"],
            audience=settings.entra_api_audience,
            issuer=issuer,
            options={
                "require": [
                    "exp",
                    "nbf",
                    "iat",
                    "iss",
                    "aud",
                    "tid",
                    "oid",
                    "ver",
                ]
            },
            leeway=30,
        )

    except (PyJWTError, ValueError) as exc:
        raise TokenValidationError(
            "Invalid or expired access token."
        ) from exc

    if claims.get("ver") != "2.0":
        raise TokenValidationError(
            "Unsupported access token version."
        )

    if claims.get("tid") != settings.entra_tenant_id:
        raise TokenValidationError(
            "Token belongs to an unexpected tenant."
        )

    object_id = claims.get("oid")

    if not isinstance(object_id, str) or not object_id:
        raise TokenValidationError(
            "Token does not identify a user."
        )

    raw_scopes = claims.get("scp")

    if not isinstance(raw_scopes, str):
        raise TokenValidationError(
            "A delegated user access token is required."
        )

    scopes = tuple(raw_scopes.split())

    if settings.entra_required_scope not in scopes:
        raise TokenValidationError(
            "Required API scope is missing."
        )

    raw_roles = claims.get("roles", [])

    if (
        not isinstance(raw_roles, list)
        or not all(isinstance(role, str) for role in raw_roles)
    ):
        raise TokenValidationError(
            "Invalid application roles claim."
        )

    return AuthenticatedUser(
        tenant_id=claims["tid"],
        object_id=object_id,
        roles=tuple(raw_roles),
        scopes=scopes,
    )
