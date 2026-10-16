
import streamlit as st

from api_client import ask_question


st.set_page_config(
    page_title="Smart RFP Assistant",
    page_icon="📄",
    layout="wide",
)

st.title("Smart RFP Response Assistant")
st.caption("Generate evidence-based responses from historical proposals.")

question = st.text_area(
    "Enter your RFP question",
    placeholder="How does your company protect customer data?",
    height=120,
)

if st.button("Generate Answer", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching documents and generating response..."):
            try:
                result = ask_question(question)

                st.subheader("Generated Answer")
                st.markdown(result["answer"])

                if result.get("sources"):
                    st.subheader("Sources")

                    for source in result["sources"]:
                        st.write(
                            f"📄 {source['source_file']} "
                            f"(Page: {source['page']})"
                        )

            except Exception as error:
                st.error(f"Unable to generate answer: {error}")
