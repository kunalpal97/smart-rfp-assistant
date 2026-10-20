# Smart RFP Assistant

This is a frontend-only refactor. It keeps the existing backend routes and response fields:

- `POST /api/questions/ask`
- `GET /api/documents`
- `POST /api/documents/upload`
- `DELETE /api/documents/{document_id}`

## Folder layout

```text
frontend/
├── app.py
├── api/
│   ├── __init__.py
│   └── client.py
├── components/
│   ├── __init__.py
│   ├── confirmations.py
│   └── feedback.py
├── views/
│   ├── __init__.py
│   ├── ask_question.py
│   └── knowledge_library.py
├── .streamlit/
│   └── config.toml
├── .env.example
└── requirements.txt
```

## Run locally

1. Start the FastAPI backend as you normally do, listening on `127.0.0.1:8000`.
2. Open a second terminal and enter the frontend folder:

   ```bash
   cd ~/smart-rfp-assistant/frontend
   ```

3. Activate the virtual environment used for the frontend, or create one if needed:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

4. If the backend is at its local default, run:

   ```bash
   streamlit run app.py
   ```

   If it runs at a different address, set the environment variable before launching Streamlit:

   ```bash
   export API_BASE_URL="http://127.0.0.1:8000"
   streamlit run app.py
   ```

`.env.example` is a reference template; it is not automatically loaded because this scaffold intentionally does not add a dotenv dependency.

## Integration notes

- Copy the files into the existing `frontend/` folder after backing up or committing your current version.
- The new imports assume you launch Streamlit from inside `frontend/` (`streamlit run app.py`).
- The file uploader's key changes after a successful upload, so the selected file is reset.
- Delete requests are not sent until the user confirms in the modal.
- Network, timeout, HTTP, and malformed-response errors are normalized in `api/client.py`.
- Expected API errors are shown to the user. Unexpected exceptions are logged, while the UI displays a generic message instead of leaking an unhandled exception.
- The horizontal workspace selector renders only the active view. This avoids making the document-list API request every time a question is submitted.
- Keep backend validation and the backend's 10 MB size limit; the frontend upload limit is a convenience, not a security boundary.