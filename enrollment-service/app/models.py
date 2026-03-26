from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from datetime import datetime
from .database import Base

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, nullable=False)
    course_id = Column(String, nullable=False)
    enrolled_date = Column(DateTime, default=datetime.utcnow)