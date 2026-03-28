import uvicorn
from fastapi import FastAPI
import models
from database import engine
from routes import router

# Creates the tables in MySQL
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Review Service")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
