from sqlalchemy import Column, Integer, String, Text
from database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    course_id = Column(Integer, index=True)
    comment = Column(Text)