from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE enrollment
@router.post("/enrollments", response_model=schemas.Enrollment)
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    db_enrollment = models.Enrollment(**enrollment.dict())
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

# READ all enrollments
@router.get("/enrollments", response_model=list[schemas.Enrollment])
def list_enrollments(db: Session = Depends(get_db)):
    return db.query(models.Enrollment).all()

# READ single enrollment by ID
@router.get("/enrollments/{enrollment_id}", response_model=schemas.Enrollment)
def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return db_enrollment

# UPDATE enrollment
@router.put("/enrollments/{enrollment_id}", response_model=schemas.Enrollment)
def update_enrollment(enrollment_id: int, enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    db_enrollment.student_id = enrollment.student_id
    db_enrollment.course_id = enrollment.course_id
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

# DELETE enrollment
@router.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    db.delete(db_enrollment)
    db.commit()
    return {"detail": f"Enrollment {enrollment_id} deleted successfully"}