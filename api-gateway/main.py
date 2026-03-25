from routes import router
from fastapi import FastAPI


app = FastAPI(
    title="API Gateway",
    description="API Gateway for Online Learning Platform Microservices MVP",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "API Gateway is running",
        "services": {
            "user_service": "http://127.0.0.1:8001",
            "course_service": "http://127.0.0.1:8002",
        }
    }

app.include_router(router)