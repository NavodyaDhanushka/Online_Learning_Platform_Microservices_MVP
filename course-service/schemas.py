from pydantic import BaseModel, validator
import re

# 1. How data should look when someone CREATES a new course
class CourseCreate(BaseModel):
    title: str
    description: str

    @validator("title", "description")
    def no_special_characters(cls, value):
        # Uses regex to ensure the string contains only letters, numbers, and spaces.
        if not re.match(r"^[a-zA-Z0-9\s]+$", value):
            raise ValueError("Field must not contain special characters")
        return value

# 2. How data should look when we RETURN a course to the user
class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    instructor_id: int

    # This config tells Pydantic to translate our SQLAlchemy model 
    # into a standard JSON internet response automatically
    class Config:
        from_attributes = True