
import streamlit as st

from api.client import APIError


def show_success(message: str) -> None:
    st.success(message, icon="✅")


def show_info(message: str) -> None:
    st.info(message, icon="ℹ️")


def show_warning(message: str) -> None:
    st.warning(message, icon="⚠️")


def show_api_error(error: Exception) -> None:
    """Display expected API errors without exposing internals."""

    if isinstance(error, APIError):
        st.error(str(error), icon="🚨")
        return

    # Unexpected exceptions should be logged server-side,
    # not displayed with potentially sensitive details.
    st.error(
        "Something went wrong. Please try again. "
        "If the issue continues, check the application logs.",
        icon="🚨",
    )
    st.exception(error) if st.session_state.get(
        "debug_mode", False
    ) else None
