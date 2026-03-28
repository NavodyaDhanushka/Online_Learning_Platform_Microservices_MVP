from pydantic import BaseModel, EmailStr


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


# ---------------- ENROLLMENT SCHEMAS ----------------

class EnrollmentCreate(BaseModel):
    course_id: int


# ---------------- REVIEW SCHEMAS ----------------

class ReviewCreate(BaseModel):
    course_id: int
    comment: str


class ReviewUpdate(BaseModel):
    comment: str