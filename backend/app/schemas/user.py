
from pydantic import BaseModel, ConfigDict


class CurrentUserResponse(BaseModel):
    """Authenticated user information returned by the API."""

    model_config = ConfigDict(frozen=True)

    tenant_id: str
    object_id: str
    roles: list[str]
    scopes: list[str]
