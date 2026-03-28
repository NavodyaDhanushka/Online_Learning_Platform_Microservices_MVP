from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

import models, schemas
from database import SessionLocal
from auth import require_instructor

router = APIRouter(tags=["Courses"])

ENROLLMENT_SERVICE_URL = "http://127.0.0.1:8012"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- CREATE COURSE ----------------
@router.post("/courses/", response_model=schemas.CourseResponse)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_instructor)
):
    db_course = models.Course(
        title=course.title,
        description=course.description,
        instructor_id=current_user["id"]
    )

    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    return db_course


# ---------------- GET ALL COURSES ----------------
@router.get("/courses/", response_model=list[schemas.CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()


# ---------------- GET COURSES BY INSTRUCTOR ----------------
@router.get("/courses/instructor/{instructor_id}", response_model=list[schemas.CourseResponse])
def get_courses_by_instructor(
    instructor_id: int,
    db: Session = Depends(get_db)
):
    courses = db.query(models.Course).filter(
        models.Course.instructor_id == instructor_id
    ).all()

    return courses


# ---------------- GET SINGLE COURSE ----------------
@router.get("/courses/{course_id}", response_model=schemas.CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(models.Course).filter(
        models.Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return course


# ---------------- UPDATE COURSE ----------------
@router.put("/courses/{course_id}", response_model=schemas.CourseResponse)
def update_course(
    course_id: int,
    updated_course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_instructor)
):
    course = db.query(models.Course).filter(
        models.Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.instructor_id != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own course"
        )

    course.title = updated_course.title
    course.description = updated_course.description

    db.commit()
    db.refresh(course)

    return course


# ---------------- DELETE COURSE ----------------
@router.delete("/courses/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_instructor)
):
    course = db.query(models.Course).filter(
        models.Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.instructor_id != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own course"
        )

    db.delete(course)
    db.commit()

    return {"message": "Course deleted successfully"}


# ---------------- GET ENROLLED STUDENTS ----------------
@router.get("/courses/{course_id}/students")
async def get_enrolled_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_instructor)
):
    course = db.query(models.Course).filter(
        models.Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.instructor_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ENROLLMENT_SERVICE_URL}/enrollments/course/{course_id}"
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Enrollment service unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Enrollment service error"
        )

    return response.json()