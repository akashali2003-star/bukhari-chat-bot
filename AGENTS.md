# Project Guidance

## Overview

- This repository is a small terminal-based Python chat client powered by Gemini.
- `main.py` owns the interactive CLI loop and exit handling.
- `src/agent.py` owns model configuration, chat session setup, prompt handling, and response formatting.
- `src/__init__.py` is the package export surface; keep it minimal and avoid moving business logic there.

## Runtime and Setup

- Run the app with `python main.py` from the project root.
- On Windows, use `py main.py` if `python` is not on `PATH`.
- Install the runtime dependencies before running the app: `google-generativeai` and `python-dotenv`.
- There is no test suite, package manifest, or lockfile in this repo yet, so validation is primarily manual CLI verification.

## Configuration and Security

- Put the API key in the project-root `.env` file using the exact form `GEMINI_API_KEY=...`.
- The app loads `.env` with `load_dotenv(PROJECT_ROOT / ".env")` at import time, so code that imports `src.agent` must have the environment set before import.
- If the SDK says no API key was found, check the process working directory and confirm the root-level `.env` file is being read.
- Keep `.env` untracked and never print, commit, or paste the API key into source, logs, or documentation.
- If an API key is ever exposed in chat, logs, or source control, rotate it immediately before continuing.
- The current Gemini model name is configured in `src/agent.py`; keep provider-specific behavior there rather than scattering it across the app.
- The existing `google.generativeai` integration may emit deprecation warnings; switching to the newer Google Gen AI SDK should be treated as an intentional compatibility change, not a silent refactor.

## Code Conventions

- Follow type annotations and keep the dataclass-based `ChatMessage` pattern when adding message state.
- Keep user-facing API failures as plain response strings unless the public CLI contract is intentionally changing.
- Preserve the CLI exit commands exactly: `exit`, `quit`, and `bye`.
- Keep application logic inside `src/`; keep `main.py` focused on terminal I/O and the main prompt loop.
- Although `BasicAgent` stores a `history` list, avoid changing behavior without considering the active `genai` chat session and empty-prompt handling.

## Validation Checklist

Before claiming a runtime change is valid, run the CLI with a valid local `GEMINI_API_KEY` and confirm all of these scenarios work:

- a normal prompt
- an empty prompt, which should return the existing "I'm ready when you are." behavior
- an exit command such as `exit`, `quit`, or `bye`

When editing import-time configuration or API behavior, verify the missing-key error path still behaves as expected without requiring credentials for non-API test code.

## Good First Changes

- Small, focused changes in `src/agent.py` are preferred over broad refactors.
- If you add new state or helper methods, keep them close to the chat-agent concerns instead of mixing them into the CLI loop.
- Prefer minimal edits that preserve the current terminal UX and the model configuration ownership in the agent module.
