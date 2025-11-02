# Instagram AI Bot

Simple Flask webhook that forwards Instagram messages to an OpenRouter / OpenAI-style model and replies.

Quick start

1. Create and activate a virtual environment (macOS / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app locally (development):

```bash
python app.py
```

Notes
- Set your `PAGE_ACCESS_TOKEN`, `VERIFY_TOKEN`, and `OPENROUTER_API_KEY` securely (avoid committing secrets).
- This project contains example code for a webhook listener — configure a public HTTPS endpoint (ngrok, cloud) for Meta to call.

License: MIT
