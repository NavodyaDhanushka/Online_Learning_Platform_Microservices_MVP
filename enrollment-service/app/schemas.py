from pydantic import BaseModel
from datetime import datetime

class EnrollmentBase(BaseModel):
    student_id: str
    course_id: str

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    id: int
    enrolled_date: datetime

    class Config:
        from_attributes = True