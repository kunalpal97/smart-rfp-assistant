
import streamlit as st

from api.client import delete_document
from components.feedback import show_api_error, show_success


@st.dialog("Delete document", width="small")
def confirm_delete_dialog(document: dict) -> None:
    """Ask for explicit confirmation before deleting a document."""

    filename = document.get("filename", "this document")
    document_id = document.get("document_id")

    st.write(f"Are you sure you want to delete **{filename}**?")

    st.warning(
        "This removes the document from the library. "
        "Make sure you no longer need it before continuing."
    )

    st.caption("This action cannot be undone from this screen.")

    confirm_col, cancel_col = st.columns(2)

    with confirm_col:
        if st.button(
            "Delete permanently",
            type="primary",
            use_container_width=True,
            key=f"confirm-delete-{document_id}",
        ):
            if not document_id:
                st.error("Cannot delete this document: its ID is missing.")
                return

            try:
                result = delete_document(str(document_id))
                show_success(
                    result.get("message", "Document deleted successfully.")
                )
                st.session_state["refresh_documents"] = True
                st.rerun()

            except Exception as error:
                show_api_error(error)

    with cancel_col:
        if st.button(
            "Cancel",
            use_container_width=True,
            key=f"cancel-delete-{document_id}",
        ):
            st.rerun()
