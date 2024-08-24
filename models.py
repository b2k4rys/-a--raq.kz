from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from typing import List
from database import Base


class User(Base):
  __tablename__ = "users"

    
  id = Column(Integer, autoincrement=True, primary_key=True)
  username = Column(String(25), unique=True)
  password = Column(String(10))
  name = Column(String(50))
  city = Column(String)
  phone = Column(String(20), unique=True)

  houses = relationship('House', backref='users')


class House(Base):
  __tablename__ = 'houses'

  id = Column(Integer, autoincrement=True, primary_key=True)
  owner_id = Column(Integer(), ForeignKey('users.id'))

  type = Column(String(10))
  price = Column(Integer)
  address = Column(Text)
  area = Column(Float)
  rooms_count = Column(Integer)
  description = Column(Text)

  comments = relationship('Comment', backref='houses')


class Comment(Base):
  __tablename__ = 'comments'

  id = Column(Integer, autoincrement=True, primary_key=True)
  house_id =  Column(Integer(), ForeignKey('houses.id'))
  
  content = Column(Text)
  created_at = Column(Text)
  author_id = Column(Integer())


