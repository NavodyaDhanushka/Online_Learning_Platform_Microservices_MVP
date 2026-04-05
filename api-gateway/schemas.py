import re

from pydantic import BaseModel, EmailStr, field_validator


# ---------------- USER SCHEMAS ----------------

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    role: str


# ---------------- COURSE SCHEMAS ----------------

class CourseCreate(BaseModel):
    title: str
    description: str

    @field_validator("title", "description")
    @classmethod
    def no_special_characters(cls, value: str) -> str:
        if not re.match(r"^[a-zA-Z0-9\s]+$", value):
            raise ValueError("Field must not contain special characters")
        return value


# ---------------- ENROLLMENT SCHEMAS ----------------

class EnrollmentCreate(BaseModel):
    course_id: int


# ---------------- REVIEW SCHEMAS ----------------

class ReviewCreate(BaseModel):
    course_id: int
    comment: str


class ReviewUpdate(BaseModel):
    comment: str