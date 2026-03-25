from sqlalchemy import Column, Integer, String, Text
from database import Base

class Course(Base):
    # This is the actual name of the table that will appear in MySQL
    __tablename__ = "courses"

    # These are the columns inside the table
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(Text)
    
    # This stores the ID of the user who made the course 
    # (Later, this is how you'll link up with your friend's user-service)
    instructor_id = Column(Integer)