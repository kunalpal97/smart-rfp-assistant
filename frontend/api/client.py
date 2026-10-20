
import os
from typing import Any

import requests


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


class APIError(Exception):
    """A readable error returned by an API operation."""


def _request(
    method: str,
    path: str,
    *,
    timeout: int = 30,
    **kwargs: Any,
) -> dict:
    """Send an HTTP request and validate its response."""

    url = f"{API_BASE_URL}{path}"

    try:
        response = requests.request(
            method,
            url,
            timeout=timeout,
            **kwargs,
        )

    except requests.Timeout as error:
        raise APIError(
            "The server took too long to respond. Please try again."
        ) from error

    except requests.ConnectionError as error:
        raise APIError(
            "Cannot connect to the Smart RFP server. "
            "Check that the backend is running."
        ) from error

    except requests.RequestException as error:
        raise APIError(
            "A network error occurred. Please try again."
        ) from error

    if not response.ok:
        detail = ""

        try:
            payload = response.json()
            detail = payload.get("detail", "")

            if isinstance(detail, (dict, list)):
                detail = ""
        except ValueError:
            pass

        safe_messages = {
            400: "The request could not be processed.",
            401: "Authentication is required.",
            403: "You do not have permission to perform this action.",
            404: "The requested resource was not found.",
            413: "The uploaded file is too large.",
            422: "Some submitted information is invalid.",
            429: "Too many requests. Please wait and try again.",
        }

        message = safe_messages.get(
            response.status_code,
            (
                "The server encountered an error."
                if response.status_code >= 500
                else "The request failed."
            ),
        )

        if detail and response.status_code < 500:
            message = str(detail)

        raise APIError(
            f"{message} (HTTP {response.status_code})"
        )

    try:
        payload = response.json()
    except ValueError as error:
        raise APIError(
            "The server returned an invalid response."
        ) from error

    if not isinstance(payload, dict):
        raise APIError(
            "The server returned an unexpected response format."
        )

    return payload


def ask_question(question: str) -> dict:
    return _request(
        "POST",
        "/api/questions/ask",
        json={"question": question},
        timeout=120,
    )


def list_documents() -> dict:
    return _request(
        "GET",
        "/api/documents",
        timeout=30,
    )


def upload_document(uploaded_file) -> dict:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }

    return _request(
        "POST",
        "/api/documents/upload",
        files=files,
        timeout=180,
    )


def delete_document(document_id: str) -> dict:
    return _request(
        "DELETE",
        f"/api/documents/{document_id}",
        timeout=60,
    )
