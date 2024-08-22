from fastapi import FastAPI, Depends, Response
import models
from sqlalchemy.orm import Session 
from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal
from pydantic import EmailStr, Field, BaseModel
from typing import Annotated
from http import HTTPStatus


app = FastAPI()
models.Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
db_dependecy = Annotated[Session, Depends(get_db)]

class UserBase(BaseModel):
  username: EmailStr
  password: str
  name: str
  city: str
  phone: str




@app.post('/auth/users/')
async def register(db: db_dependecy, user: UserBase, response: Response):
  db_user = models.User(username=user.username, password=user.password, phone=user.phone, city=user.city, name=user.name)
  db.add(db_user)
  db.commit()
  return HTTPStatus.OK.value


