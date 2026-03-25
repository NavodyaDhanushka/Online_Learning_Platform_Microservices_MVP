from fastapi import FastAPI
from database import Base, engine
from routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    description="User microservice with JWT authentication for Online Learning Platform",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "User Service is running successfully"}

app.include_router(router)