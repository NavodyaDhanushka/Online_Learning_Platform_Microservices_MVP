import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from database import SessionLocal

router = APIRouter(tags=["Reviews"])

# =================================================================
# THE MAGIC SWITCH
# Set to True: Tests the Review service by itself (skips network checks).
# Set to False: Connects to the real User and Course services.
# =================================================================
STANDALONE_MODE = True 

USER_SERVICE_URL = "http://localhost:8001"
COURSE_SERVICE_URL = "http://localhost:8000"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/reviews/", response_model=schemas.ReviewResponse)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    
    # --- IF STANDALONE MODE IS OFF, DO THE REAL CHECKS ---
    if not STANDALONE_MODE:
        # 1. CHECK THE USER SERVICE
        try:
            user_response = requests.get(f"{USER_SERVICE_URL}/users/{review.student_id}")
            if user_response.status_code == 404:
                raise HTTPException(status_code=404, detail="Student ID does not exist in User Service.")
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail="User Service is currently down.")

        # 2. CHECK THE COURSE SERVICE
        try:
            course_response = requests.get(f"{COURSE_SERVICE_URL}/courses/{review.course_id}")
            if course_response.status_code == 404:
                 raise HTTPException(status_code=404, detail="Course ID does not exist in Course Service.")
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail="Course Service is currently down.")
    else:
        print("STANDALONE MODE IS ON: Bypassing external checks!")

    # --- SAVE TO DATABASE ---
    new_review = models.Review(
        student_id=review.student_id,
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

# UPDATE A REVIEW
@router.put("/reviews/{review_id}", response_model=schemas.ReviewResponse)
def update_review(review_id: int, review_update: schemas.ReviewUpdate, db: Session = Depends(get_db)):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    db_review.comment = review_update.comment
    db.commit()
    db.refresh(db_review)
    return db_review

# DELETE A REVIEW
@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    db.delete(db_review)
    db.commit()
    return {"message": "Review deleted successfully"}