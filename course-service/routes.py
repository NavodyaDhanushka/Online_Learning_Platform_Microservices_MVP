from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal

router = APIRouter(tags=["Courses"])

# Dependency: This is like a temporary tunnel to your database for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---

# 1. CREATE A COURSE (POST)
@router.post("/courses/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    # Create the database record using the data passed the Pydantic bouncer
    db_course = models.Course(
        title=course.title,
        description=course.description,
        instructor_id=course.instructor_id
    )
    # Add it, save it, and refresh it to get the new ID
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# 2. GET ALL COURSES (GET)
@router.get("/courses/", response_model=list[schemas.CourseResponse])
def read_courses(db: Session = Depends(get_db)):
    # Ask the database for all the courses
    courses = db.query(models.Course).all()
    return courses
