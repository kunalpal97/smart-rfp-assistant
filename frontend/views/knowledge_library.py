
import streamlit as st

from api.client import (
    list_documents,
    upload_document,
)
from components.confirmations import confirm_delete_dialog
from components.feedback import (
    show_api_error,
    show_info,
    show_success,
    show_warning,
)


def render_knowledge_library() -> None:
    """Render the document library and upload workflow."""

    st.title("Knowledge Library")
    st.markdown(
        '<p class="muted-copy">Manage the historical proposals '
        "used to ground your RFP responses.</p>",
        unsafe_allow_html=True,
    )

    st.write("")

    # ----------------------------
    # Upload panel
    # ----------------------------

    with st.container(border=True):
        st.subheader("Add a reference document")
        st.caption(
            "Upload a PDF, plain-text file, or Markdown proposal "
            "to make its content available for retrieval."
        )

        if "uploader_version" not in st.session_state:
            st.session_state["uploader_version"] = 0

        with st.form("document_upload_form", clear_on_submit=False):
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["pdf", "txt", "md"],
                key=(
                    f"document-uploader-"
                    f"{st.session_state['uploader_version']}"
                ),
                help="Maximum file size: 10 MB.",
            )

            submitted = st.form_submit_button(
                "Upload and index document",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if uploaded_file is None:
                show_warning("Choose a document before uploading.")

            elif uploaded_file.size > 10 * 1024 * 1024:
                show_warning(
                    "The selected file exceeds the 10 MB limit."
                )

            else:
                try:
                    with st.spinner(
                        "Uploading document and building its index..."
                    ):
                        result = upload_document(uploaded_file)

                    show_success(
                        result.get(
                            "message",
                            "Document uploaded and indexed successfully.",
                        )
                    )

                    st.session_state["uploader_version"] += 1
                    st.session_state["refresh_documents"] = True
                    st.rerun()

                except Exception as error:
                    show_api_error(error)

    st.write("")

    # ----------------------------
    # Existing documents
    # ----------------------------

    header_col, refresh_col = st.columns([5, 1])

    with header_col:
        st.subheader("Your documents")
        st.caption(
            "Reference material currently registered in the library."
        )

    with refresh_col:
        st.write("")
        refresh_clicked = st.button(
            "↻ Refresh",
            use_container_width=True,
            key="refresh-document-list",
        )

    refresh_requested = st.session_state.pop(
        "refresh_documents", False
    )

    if refresh_clicked or refresh_requested or (
        "documents_cache" not in st.session_state
    ):
        try:
            with st.spinner("Loading documents..."):
                result = list_documents()

            documents = result.get("documents", [])

            if not isinstance(documents, list):
                raise ValueError(
                    "The document list has an unexpected format."
                )

            st.session_state["documents_cache"] = documents

        except Exception as error:
            show_api_error(error)

            if "documents_cache" not in st.session_state:
                return

    documents = st.session_state.get("documents_cache", [])

    total_documents = len(documents)

    total_chunks = sum(
        document.get("chunk_count", 0) or 0
        for document in documents
    )

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        with st.container(border=True):
            st.metric("Indexed documents", total_documents)

    with metric_col2:
        with st.container(border=True):
            st.metric("Indexed chunks", total_chunks)

    st.write("")

    if not documents:
        with st.container(border=True):
            st.markdown("### Your library is empty")
            st.write(
                "Upload your first historical proposal to start "
                "building a searchable knowledge base."
            )
        return

    # ----------------------------
    # Document cards
    # ----------------------------

    for document in documents:
        filename = document.get("filename", "Untitled document")
        document_id = document.get("document_id")

        with st.container(border=True):
            details_col, action_col = st.columns(
                [5, 1],
                vertical_alignment="center",
            )

            with details_col:
                st.markdown(f"**📄 {filename}**")
                st.caption(
                    f"{document.get('chunk_count', 0)} indexed chunks"
                )

            with action_col:
                if st.button(
                    "Delete",
                    key=f"delete-document-{document_id}",
                    use_container_width=True,
                    disabled=not document_id,
                ):
                    confirm_delete_dialog(document)
