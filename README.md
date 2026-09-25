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

Set `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, and `SUPABASE_REDIRECT_URL` in `.env`. For Streamlit deployment, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` or add the same keys in the deployment secrets UI.

## Supabase setup

Run [`supabase_schema.sql`](supabase_schema.sql) in the Supabase SQL Editor. Email authentication must also be enabled in Supabase Authentication settings. The app supports email/password, Google OAuth, and guest sessions; guest chats remain session-only until the user signs in and chooses to save them.

The app accepts either the project URL (`https://<project-ref>.supabase.co`) or the REST URL ending in `/rest/v1/`; it normalizes the latter automatically.

### Google Sign-In setup

1. In Google Cloud Console, create or select a project and configure the OAuth consent screen. Add the required app name, support email, developer contact, and test users if the app is still in testing.
2. Create an OAuth Client ID under **APIs & Services > Credentials > Create credentials > OAuth client ID**, choosing **Web application**.
3. In Supabase, open **Authentication > Providers > Google**, enable Google, and paste the Google **Client ID** and **Client Secret**.
4. In Google Cloud Console, add this exact authorized redirect URI:
	`https://<project-ref>.supabase.co/auth/v1/callback`
5. In Supabase, open **Authentication > URL Configuration** and add the deployed app URL (the value used for `SUPABASE_REDIRECT_URL`) to **Redirect URLs**. For local testing, add `http://localhost:8501/app/`.
6. Set `SUPABASE_REDIRECT_URL` to the URL users should return to after Google login, then restart/redeploy the app.

## Terminal client

```bash
py main.py
```

## Example

```text
You> hello
Agent> ...
```
