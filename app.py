import os
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib

# ---------- Page setup ----------
st.set_page_config(page_title="Affiliate Marketing Chatbot", page_icon="💬")
st.title("💬 Affiliate Marketing Chatbot")
st.caption("Ask anything about affiliate marketing. Answers come from the built-in knowledge guide.")

# ---------- Config ----------
# Looks for the key in this order:
#   1. Streamlit secrets (.streamlit/secrets.toml in the launch folder, or Cloud Secrets)
#   2. .streamlit/secrets.toml next to app.py (works from any launch folder)
#   3. GEMINI_API_KEY / GEMINI_MODEL environment variables
def load_config():
    try:
        return st.secrets["gemini"]["api_key"], st.secrets["gemini"].get("model", DEFAULT_MODEL)
    except Exception:
        pass
    local = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if local.exists():
        try:
            gem = tomllib.loads(local.read_text(encoding="utf-8")).get("gemini", {})
            if gem.get("api_key"):
                return gem["api_key"], gem.get("model", DEFAULT_MODEL)
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY"), os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)


DEFAULT_MODEL = "gemini-3.5-flash-lite"
API_KEY, MODEL_NAME = load_config()
if not API_KEY:
    st.error(
        "Gemini API key not found. Add it to `.streamlit/secrets.toml` under the "
        "`[gemini]` section (see README.md), or set the GEMINI_API_KEY environment variable."
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
