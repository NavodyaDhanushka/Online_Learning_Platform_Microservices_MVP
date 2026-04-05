import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import create_access_token, hash_password, verify_password
from database import get_db
from dependencies import get_current_user, require_instructor
from models import User
from schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)

router = APIRouter(tags=["Users"])

COURSE_SERVICE_URL = "http://127.0.0.1:8011"
ENROLLMENT_SERVICE_URL = "http://127.0.0.1:8012"


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/auth/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/users/me", response_model=UserResponse)
def get_logged_in_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users/me/courses")
async def get_my_courses(current_user: User = Depends(require_instructor)):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{COURSE_SERVICE_URL}/courses/instructor/{current_user.id}"
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Could not fetch instructor courses from Course Service"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Course Service is unavailable"
        )


@router.get("/users/me/enrolled-courses")
async def get_my_enrolled_courses(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view enrolled courses"
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Step 1: get student's enrollments
            enroll_response = await client.get(
                f"{ENROLLMENT_SERVICE_URL}/enrollments/student/{current_user.id}"
            )

            if enroll_response.status_code != 200:
                raise HTTPException(
                    status_code=enroll_response.status_code,
                    detail="Could not fetch student enrollments from Enrollment Service"
                )

            enrollments = enroll_response.json()

            # Step 2: get full course details for each enrolled course
            enrolled_courses = []

            for enrollment in enrollments:
                course_id = enrollment["course_id"]

                course_response = await client.get(
                    f"{COURSE_SERVICE_URL}/courses/{course_id}"
                )

                if course_response.status_code == 200:
                    enrolled_courses.append(course_response.json())

            return enrolled_courses

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dependent service is unavailable"
        )


@router.put("/users/me", response_model=UserResponse)
def update_my_profile(
    updated_user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_email = (
        db.query(User)
        .filter(User.email == updated_user.email, User.id != current_user.id)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    current_user.name = updated_user.name
    current_user.email = updated_user.email
    current_user.role = updated_user.role

    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Instructor cannot delete another instructor
    if user.role == "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructors cannot delete other instructors"
        )

    # Only students can be deleted
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can be deleted"
        )

    db.delete(user)
    db.commit()

    return {"message": "Student deleted successfully"}