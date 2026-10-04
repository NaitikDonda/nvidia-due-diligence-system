
import streamlit as st
import json
import os

st.set_page_config(
    page_title="NVIDIA Financial Research",
    page_icon="N",
    layout="wide"
)

st.title("NVIDIA Financial Research System")
st.caption("AI-powered financial research and due-diligence engine")

query = st.text_input(
    "Ask a question about NVIDIA",
    placeholder="Should I invest in NVIDIA?"
)

if st.button("Analyze") and query.strip():

    try:

        result = generate_final_response(query)

        st.markdown("### Analysis")

        st.write(result)

    except Exception as e:

        st.error(str(e))
