from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
import requests
from auth import require_student  # 👈 import this

router = APIRouter()

COURSE_SERVICE_URL = "http://127.0.0.1:8011"

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ CREATE enrollment (ONLY students)
@router.post("/enrollments", response_model=schemas.Enrollment)
def create_enrollment(
    enrollment: schemas.EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_student)
):
    student_id = int(current_user["id"])

    # 🔹 Check if course exists in Course Service
    response = requests.get(f"{COURSE_SERVICE_URL}/courses/{enrollment.course_id}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # 🔹 Check duplicate enrollment
    existing = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student_id,
        models.Enrollment.course_id == enrollment.course_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student already enrolled in this course"
        )

    db_enrollment = models.Enrollment(
        student_id=student_id,
        course_id=enrollment.course_id
    )

    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)

    return db_enrollment


# READ all enrollments
@router.get("/enrollments", response_model=list[schemas.Enrollment])
def list_enrollments(db: Session = Depends(get_db)):
    return db.query(models.Enrollment).all()

@router.get("/enrollments/check")
def check_enrollment(student_id: int, course_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student_id,
        models.Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    return {"message": "Student is enrolled"}

# READ single enrollment
@router.get("/enrollments/{enrollment_id}", response_model=schemas.Enrollment)
def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.id == enrollment_id
    ).first()

    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    return db_enrollment


# UPDATE enrollment (optional: you can also restrict this)
@router.put("/enrollments/{enrollment_id}", response_model=schemas.Enrollment)
def update_enrollment(
    enrollment_id: int,
    enrollment: schemas.EnrollmentCreate,
    db: Session = Depends(get_db)
):
    db_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.id == enrollment_id
    ).first()

    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db_enrollment.course_id = enrollment.course_id
    db.commit()
    db.refresh(db_enrollment)

    return db_enrollment


# DELETE enrollment
@router.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.id == enrollment_id
    ).first()

    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db.delete(db_enrollment)
    db.commit()

    return {"detail": f"Enrollment {enrollment_id} deleted successfully"}

@router.get("/enrollments/course/{course_id}")
def get_enrollments_by_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id
    ).all()

    return enrollments


@router.get("/enrollments/student/{student_id}")
def get_enrollments_by_student(student_id: int, db: Session = Depends(get_db)):
    enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student_id
    ).all()

    return enrollments