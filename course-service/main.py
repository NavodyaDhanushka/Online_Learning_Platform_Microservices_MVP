from fastapi import FastAPI
from database import Base, engine
from routes import router

# This line physically builds the tables in your MySQL vault based on models.py
Base.metadata.create_all(bind=engine)

# This initializes your actual API
app = FastAPI(
    title="Course Service",
    description="Course microservice for Online Learning Platform",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Course Service is running successfully"}

app.include_router(router)