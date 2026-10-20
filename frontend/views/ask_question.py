
import streamlit as st

from api.client import ask_question
from components.feedback import (
    show_api_error,
    show_warning,
)


def render_ask_question() -> None:
    """Render the RFP question and answer workflow."""

    st.title("Ask RFP Questions")
    st.markdown(
        '<p class="muted-copy">Turn your historical proposals into '
        "evidence-backed draft responses.</p>",
        unsafe_allow_html=True,
    )

    st.write("")

    # ----------------------------
    # Question composer
    # ----------------------------

    with st.container(border=True):
        st.subheader("What do you need to answer?")
        st.caption(
            "Ask a question from your RFP. The assistant will retrieve "
            "relevant evidence from your indexed proposal library."
        )

        with st.form("rfp_question_form", clear_on_submit=False):
            question = st.text_area(
                "Your question",
                placeholder=(
                    "Example: How does your company protect customer data?"
                ),
                height=140,
                max_chars=10000,
                help="Be specific to get more relevant evidence.",
            )

            submitted = st.form_submit_button(
                "Generate draft response",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        if not question or not question.strip():
            show_warning("Enter an RFP question before continuing.")

        else:
            try:
                with st.spinner(
                    "Searching your proposals and generating a response..."
                ):
                    result = ask_question(question.strip())

                st.session_state["latest_rfp_answer"] = result
                st.session_state["latest_rfp_question"] = question.strip()

            except Exception as error:
                show_api_error(error)

    # ----------------------------
    # Generated answer
    # ----------------------------

    result = st.session_state.get("latest_rfp_answer")

    if not result:
        st.write("")

        with st.container(border=True):
            st.markdown("### Your response will appear here")
            st.write(
                "Submit a question above to see the generated draft "
                "and the supporting evidence retrieved by the assistant."
            )
        return

    st.write("")
    st.subheader("Generated response")

    with st.container(border=True):
        st.caption("DRAFT RESPONSE")
        answer = result.get("answer")

        if isinstance(answer, str) and answer.strip():
            st.markdown(answer)
        else:
            st.warning(
                "The server did not return a usable answer. "
                "Please try again."
            )

        st.divider()

        if isinstance(answer, str) and answer.strip():
            st.download_button(
                "Download draft as Markdown",
                data=answer,
                file_name="rfp_response.md",
                mime="text/markdown",
                use_container_width=True,
            )

    # ----------------------------
    # Supporting evidence
    # ----------------------------

    sources = result.get("sources", [])

    st.write("")
    st.subheader("Supporting evidence")

    if not sources:
        st.info(
            "No supporting sources were returned. "
            "Review the response carefully before using it."
        )
        return

    st.caption(
        f"{len(sources)} source item(s) returned by the retrieval system."
    )

    for index, source in enumerate(sources, start=1):
        source_id = source.get("source_id", f"Source {index}")
        source_file = source.get("source_file", "Unknown document")
        evidence = source.get("evidence", "")
        page = source.get("page")
        distance = source.get("distance")

        with st.expander(
            f"📄 {source_id} · {source_file}",
            expanded=(index == 1),
        ):
            st.markdown("**Retrieved passage**")

            if evidence:
                st.write(evidence)
            else:
                st.caption("No passage text was returned.")

            metadata = []

            if page is not None:
                metadata.append(f"Page: {page}")

            if distance is not None:
                metadata.append(f"Retrieval distance: {distance}")

            if metadata:
                st.caption(" · ".join(metadata))

    st.caption(
        "Review the original proposal and verify every claim before "
        "submitting the generated response."
    )
