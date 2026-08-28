from fastapi import FastAPI

app = FastAPI(title="InsightForge API")


@app.get("/")
def home():
    return {"message": "InsightForge API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}