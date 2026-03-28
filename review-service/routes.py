import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from database import SessionLocal
from auth import get_current_user, require_student

router = APIRouter(tags=["Reviews"])

STANDALONE_MODE = False

USER_SERVICE_URL = "http://localhost:8010"
COURSE_SERVICE_URL = "http://localhost:8011"
ENROLLMENT_SERVICE_URL = "http://localhost:8012"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE REVIEW
@router.post("/reviews/", response_model=schemas.ReviewResponse)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_student)
):
    student_id = int(current_user["id"])

    if not STANDALONE_MODE:
        # 1. check course exists
        try:
            course_response = requests.get(f"{COURSE_SERVICE_URL}/courses/{review.course_id}")
            if course_response.status_code == 404:
                raise HTTPException(status_code=404, detail="Course not found")
            if course_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Could not validate course")
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail="Course Service is currently down")

        # 2. check student enrolled in this course
        try:
            enroll_response = requests.get(
                f"{ENROLLMENT_SERVICE_URL}/enrollments/check",
                params={"student_id": student_id, "course_id": review.course_id}
            )

            if enroll_response.status_code == 404:
                raise HTTPException(status_code=403, detail="Only enrolled students can create a review")

            if enroll_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Could not verify enrollment")
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail="Enrollment Service is currently down")

    # optional: prevent duplicate review for same student/course
    existing_review = db.query(models.Review).filter(
        models.Review.student_id == student_id,
        models.Review.course_id == review.course_id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="You already reviewed this course")

    new_review = models.Review(
        student_id=student_id,   # always from token
        course_id=review.course_id,
        comment=review.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


# GET ALL REVIEWS
@router.get("/reviews/", response_model=list[schemas.ReviewResponse])
def get_reviews(db: Session = Depends(get_db)):
    return db.query(models.Review).all()


# UPDATE REVIEW - only review owner student
@router.put("/reviews/{review_id}", response_model=schemas.ReviewResponse)
def update_review(
    review_id: int,
    review_update: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_student)
):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()

    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    if db_review.student_id != int(current_user["id"]):
        raise HTTPException(status_code=403, detail="You can only edit your own review")

    db_review.comment = review_update.comment
    db.commit()
    db.refresh(db_review)
    return db_review


# DELETE REVIEW - review owner student OR course owner instructor
@router.delete("/reviews/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()

    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    current_user_id = int(current_user["id"])
    current_user_role = current_user["role"]

    # student can delete own review
    if current_user_role == "student" and db_review.student_id == current_user_id:
        db.delete(db_review)
        db.commit()
        return {"message": "Review deleted successfully"}

    # instructor can delete review if they own the course
    if current_user_role == "instructor":
        if STANDALONE_MODE:
            raise HTTPException(
                status_code=403,
                detail="Instructor delete check requires Course Service when standalone mode is off"
            )

        try:
            course_response = requests.get(f"{COURSE_SERVICE_URL}/courses/{db_review.course_id}")

            if course_response.status_code == 404:
                raise HTTPException(status_code=404, detail="Course not found")

            if course_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Could not validate course ownership")

            course_data = course_response.json()

            if course_data["instructor_id"] != current_user_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only delete reviews of your own course"
                )

            db.delete(db_review)
            db.commit()
            return {"message": "Review deleted successfully"}

        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail="Course Service is currently down")

    raise HTTPException(status_code=403, detail="Not authorized to delete this review")