from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"
    # Use primary_key=True (lowercase)
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True, index=True) 

class User(Base):
    __tablename__ = "users"
    # Use primary_key=True (lowercase)
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String) 
    role_id = Column(Integer, ForeignKey("roles.id"))
    
    role = relationship("Role")