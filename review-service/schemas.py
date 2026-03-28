from pydantic import BaseModel

class ReviewCreate(BaseModel):
    course_id: int
    comment: str

class ReviewUpdate(BaseModel):
    comment: str

class ReviewResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    comment: str

    class Config:
        from_attributes = True