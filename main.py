from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def root():
    return {
        "message": "Welcome to the AI Interview System"
    }
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-interview-system"
    }