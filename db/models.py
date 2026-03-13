from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class UserRecord(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nume = Column(String, nullable=False)
    generated_name = Column(String, unique=True, nullable=False)
    content_type = Column(String, nullable=True) 
    path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # for linking the object, not only the id + file.owner.name/email
    owner = relationship("UserRecord")
