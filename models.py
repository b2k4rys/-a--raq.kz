from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
  __tablename__ = "users"

    
  id = Column(Integer, autoincrement=True, primary_key=True)
  username = Column(String(25), unique=True)
  password = Column(String(10))
  name = Column(String(50))
  city = Column(String)
  phone = Column(String(20), unique=True)