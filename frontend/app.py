
import streamlit as st

from views.ask_question import render_ask_question
from views.knowledge_library import render_knowledge_library


st.set_page_config(
    page_title="Smart RFP Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_styles() -> None:
    """Apply a consistent dark UI across the application."""

    st.markdown(
        """
        <style>
        /* Main workspace */
        .stApp {
            background: #0B1020;
            color: #E8ECF5;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #101729;
            border-right: 1px solid #273149;
        }

        section[data-testid="stSidebar"] .block-container {
            padding: 1.5rem 1rem;
        }

        /* Headings */
        h1, h2, h3 {
            color: #F3F6FC;
            letter-spacing: -0.025em;
        }

        h1 {
            font-weight: 750;
        }

        /* Supporting copy */
        p, label {
            line-height: 1.6;
        }

        /* Cards and bordered containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #141B2D;
            border: 1px solid #29344C;
            border-radius: 14px;
            padding: 4px;
        }

        /* Inputs */
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            background: #0F1729;
            color: #E8ECF5;
            border: 1px solid #34415C;
            border-radius: 10px;
        }

        /* Buttons */
        .stButton > button,
        .stFormSubmitButton > button {
            border-radius: 9px;
            min-height: 42px;
            font-weight: 600;
        }

        /* Dividers */
        hr {
            border-color: #29344C;
        }

        /* Small labels */
        .eyebrow {
            color: #9EB5FF;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.1em;
        }

        .muted-copy {
            color: #A5B0C5;
            font-size: 0.95rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


load_styles()


# Sidebar branding and navigation
with st.sidebar:
    st.markdown("## 📄 Smart RFP")
    st.caption("Proposal intelligence workspace")

    st.divider()

    st.markdown(
        '<p class="eyebrow">WORKSPACE</p>',
        unsafe_allow_html=True,
    )

    active_view = st.radio(
        "Workspace navigation",
        options=[
            "Knowledge Library",
            "Ask RFP Questions",
        ],
        format_func=lambda item: (
            "📁  Knowledge Library"
            if item == "Knowledge Library"
            else "💬  Ask RFP Questions"
        ),
        label_visibility="collapsed",
        key="active_workspace",
    )

    st.divider()

    st.markdown("**Evidence-based responses**")
    st.caption(
        "Review supporting sources before using generated answers."
    )


# Main workspace
if active_view == "Knowledge Library":
    render_knowledge_library()
else:
    render_ask_question()
