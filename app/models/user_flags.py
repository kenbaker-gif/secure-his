from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.database import Base

class UserFlags(Base):
    __tablename__ = 'user_flags'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    must_change_password = Column(Boolean, default=False)
