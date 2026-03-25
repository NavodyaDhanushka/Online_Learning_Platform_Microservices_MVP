from pydantic import BaseModel

# 1. How data should look when someone CREATES a new course
class CourseCreate(BaseModel):
    title: str
    description: str
    instructor_id: int

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