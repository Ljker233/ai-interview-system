print("LOADED app/main.py WITH CORS")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import user_router
from app.routers import interview_router

app = FastAPI(
    title="AI Interview System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-interview-system",
        "cors": "enabled",
    }


app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(interview_router.router, prefix="/interviews", tags=["Interviews"])