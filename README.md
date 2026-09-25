# Bukhari Chat Bot

This project includes a Streamlit chat UI backed by Gemini and Supabase authentication.

## Features

- Supabase email/password sign up, login, and logout
- Per-user chat history saved in Supabase
- Sidebar for starting a new chat and reopening saved exchanges
- Gemini image and text responses

## Run it

```bash
py -m pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Set `GEMINI_API_KEY`, `SUPABASE_URL`, and `SUPABASE_KEY` in `.env`. For Streamlit deployment, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` or add the same keys in the deployment secrets UI.

## Supabase setup

Run [`supabase_schema.sql`](supabase_schema.sql) in the Supabase SQL Editor. Email authentication must also be enabled in Supabase Authentication settings.

The app accepts either the project URL (`https://<project-ref>.supabase.co`) or the REST URL ending in `/rest/v1/`; it normalizes the latter automatically.

## Terminal client

```bash
py main.py
```

## Example

```text
You> hello
Agent> ...
```
