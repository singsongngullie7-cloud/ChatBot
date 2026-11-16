# Affiliate Marketing Chatbot (Streamlit)

A Streamlit chat app that answers questions about affiliate marketing using Gemini,
grounded in the knowledge guide in `manual.txt`.

## Project structure

```
affiliate_chatbot/
├── app.py                         # Streamlit app
├── manual.txt                     # Knowledge guide the chatbot answers from
├── requirements.txt
├── .gitignore
└── .streamlit/
    ├── secrets.toml               # Your API key (keep private)
    └── secrets.toml.example       # Template with a placeholder key
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## API key configuration

The key is read from `.streamlit/secrets.toml`:

```toml
[gemini]
api_key = "YOUR_GEMINI_API_KEY"
model = "gemini-3.5-flash-lite"
```

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub (`secrets.toml` is git-ignored, so it won't be uploaded).
2. Create the app on share.streamlit.io and pick `app.py` as the main file.
3. Open **App settings → Secrets** and paste the same `[gemini]` block shown above.

## Editing the knowledge base

Edit `manual.txt` and restart/rerun the app. No code change is needed.
