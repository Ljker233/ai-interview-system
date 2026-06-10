from fastapi import FastAPI

from app.routers.interview_router import router as interview_router


app = FastAPI(
    title="AI Interview System",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-interview-system"
    }


app.include_router(interview_router)