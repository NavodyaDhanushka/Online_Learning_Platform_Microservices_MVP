from fastapi import FastAPI
from routes import router
from database import Base, engine

# Create tables if not exists
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Enrollment Service Running"}