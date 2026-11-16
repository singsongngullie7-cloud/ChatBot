from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

# ---------- Page setup ----------
st.set_page_config(page_title="Affiliate Marketing Chatbot", page_icon="💬")
st.title("💬 Affiliate Marketing Chatbot")
st.caption("Ask anything about affiliate marketing. Answers come from the built-in knowledge guide.")

# ---------- Config (from .streamlit/secrets.toml) ----------
try:
    API_KEY = st.secrets["gemini"]["api_key"]
    MODEL_NAME = st.secrets["gemini"].get("model", "gemini-3.5-flash-lite")
except (KeyError, FileNotFoundError):
    st.error(
        "Gemini API key not found. Add it to `.streamlit/secrets.toml` under the "
        "`[gemini]` section (see README.md)."
    )
    st.stop()

if not API_KEY or API_KEY.startswith("PASTE_"):
    st.error("Please replace the placeholder in `.streamlit/secrets.toml` with your real Gemini API key.")
    st.stop()

SYSTEM_INSTRUCTION = """Answer only from the given manual.
If the answer is not available in the manual, say: Information not available.
Give simple and clear answers."""


# ---------- Cached resources ----------
@st.cache_resource
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


@st.cache_data
def load_manual() -> str:
    return (Path(__file__).parent / "manual.txt").read_text(encoding="utf-8")


client = get_client(API_KEY)
manual = load_manual()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Options")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.caption(f"Model: `{MODEL_NAME}`")

# ---------- Chat history ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Chat input ----------
question = st.chat_input("Ask your question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=manual + "\n\nQuestion: " + question,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
                )
                answer = response.text or "Information not available."
            except Exception as e:
                answer = f"⚠️ Something went wrong while contacting Gemini: `{e}`"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
