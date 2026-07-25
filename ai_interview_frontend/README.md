# AI Interview Frontend

Simple React + Vite frontend for the AI Interview FastAPI backend.

## Supported backend APIs

```http
GET /health
POST /users
POST /interviews
GET /users/{user_id}/interviews
GET /interviews/{interview_id}/details
POST /interviews/{interview_id}/questions/{question_id}/answer
```

## Run

```bash
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Default backend URL:

```text
http://localhost:8000
```

You can change the backend URL in the UI.

## Backend CORS requirement

If frontend runs on `localhost:5173` and backend runs on `localhost:8000`, FastAPI needs CORS.

Add this to `app/main.py` after creating `app = FastAPI(...)`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For quick classroom testing only, you can use:

```python
allow_origins=["*"]
```

## Test flow

1. Start backend:

```bash
python -m uvicorn app.main:app --reload --log-level debug
```

2. Start frontend:

```bash
npm run dev
```

3. Click `Test /health`.

4. Create user.

5. Create interview.

6. Run question generation worker:

```bash
python -m app.workers.question_generation_listener
```

7. Click `Load Details`.

8. Submit an answer.

9. Run answer evaluation worker:

```bash
python -m app.workers.answer_evaluation_listener
```

10. Click `Refresh`.

## Notes

If `question_id` contains `#`, this frontend uses `encodeURIComponent`, so the URL is encoded correctly.
