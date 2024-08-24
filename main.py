from fastapi import Depends, FastAPI, Response, Form, Cookie, status, HTTPException
import models
from sqlalchemy.orm import Session 
from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal
from pydantic import EmailStr, Field, BaseModel
from typing import Annotated
from http import HTTPStatus
import jwt
import datetime
from fastapi.responses import JSONResponse

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

class HouseBase(BaseModel):

  type: str
  price: int
  address: str
  area: float | int
  rooms_count: int
  description: str

class CommentBase(BaseModel):
  content: str






def create_jwt(user_id: int):
   body = {"user_id": user_id}
   token = jwt.encode(body, "", "HS256")
   return token

def decode_jwt(token):
   data = jwt.decode(token, "", "HS256")
   return data["user_id"]





@app.post('/auth/users/')
async def register(user: UserBase, response: Response):
  db = SessionLocal()
  db_user = models.User(username=user.username, password=user.password, phone=user.phone, city=user.city, name=user.name)
  db.add(db_user)
  db.commit()
  return HTTPStatus.OK.value





@app.post("/auth/users/login")
async def login(username: str = Form(), password: str = Form()):
  db = SessionLocal()
  user  = db.query(models.User).filter(models.User.username == username).first()
  if user.password == password:
    token = create_jwt(user.id)
    response = Response('logged in')
    response.set_cookie("token", token)
    return {"access_token": token}
  return Response("Persmission denied")




@app.get("/auth/users/me")
async def get_user_data(token: str = Cookie()):
  db = SessionLocal()
  user_id = decode_jwt(token)
  user = db.query(models.User).filter(models.User.id == user_id).first()

  return {
    "id": user.id,
    "username": user.username,
    "phone": user.phone, 
    "name": user.name,
    "city": user.city
  }

@app.post("/auth/users/me")
async def update_user_data(phone: str, name: str, city: str,response: Response, token: str = Cookie()):
  db = SessionLocal()
  user_id = decode_jwt(token)
  user = db.query(models.User).filter(models.User.id == user_id).first()
  user.name = name
  user.city = city
  user.phone = phone
  db.commit()
  return response.status_code

@app.post("/shanyraks/")
async def create_house_ad(house: HouseBase, token: str = Cookie()):
  db = SessionLocal()
  owner_id = decode_jwt(token)
  db_house = models.House(type=house.type, price=house.price, address=house.address, area=house.area, rooms_count=house.rooms_count, description=house.description, owner_id=owner_id)
  db.add(db_house)
  db.commit()
  return HTTPStatus.OK.value

@app.get('/shanyraks/{id}')
async def get_house_by_id(id: int):
  db = SessionLocal()
  db_house = db.query(models.House).filter(models.House.id == id).first()
  return db_house

@app.get("/shanyraks/users/{owner_id}")
async def get_houses_by_owner_id(owner_id: int):
  db = SessionLocal()
  db_houses = db.query(models.House).filter(models.House.owner_id == owner_id).all()
  return db_houses

@app.put('/shanyraks/{id}')
async def update_house_by_id(id: int, type: str, price: int, address: str, area: float, rooms_count: int, description: str, token: str = Cookie()):
  db = SessionLocal()
  owner_id = decode_jwt(token)
  db_house = db.query(models.House).filter(models.House.id == id, models.User.id == owner_id).first()
  db_house.type = type
  db_house.price = price
  db_house.address = address
  db_house.area = area
  db_house.rooms_count = rooms_count
  db_house.description = description
  db.commit()
  return HTTPStatus.OK.value

@app.delete('/shanyraks/{id}')
async def delete_house_by_id(id: int, token: str = Cookie()):
  db = SessionLocal()
  owner_id = decode_jwt(token)
  db_house = db.query(models.House).filter(models.House.id == id, models.User.id == owner_id).first()
  db.delete(db_house)
  db.commit()
  return {"message": "Item deleted successfully"}

@app.post("/shanyraks/{id}/comments")
async def comment_post(id: int, comment: CommentBase, token: str = Cookie()):
  db = SessionLocal()
  user_id = decode_jwt(token)
  db_house = db.query(models.House).filter(models.House.id == id).first()
  now = str(datetime.datetime.now())

  if db_house:
    user_comment = models.Comment(content=comment.content, created_at=now, author_id = user_id, house_id=id)
    db.add(user_comment)
    db.commit()
    return JSONResponse(content={"message": "Operation successful"}, status_code=status.HTTP_200_OK)
  else:
    return {"message": "house not found"}
  

@app.get("/shanyraks/{id}/comments")
async def get_comment(id: int):
  db = SessionLocal()
  comments = db.query(models.House).filter(models.House.id == id).all() 
  return {"comments": [comments]} 

@app.put("/shanyraks/{id}/comments")
async def update_comments(id: int, comment_id: int, content: str, token: str = Cookie()):
  db = SessionLocal()
  owner_id = decode_jwt(token)
  comment = db.query(models.Comment).filter(models.Comment.id == comment_id, models.Comment.house_id == id, models.Comment.author_id == owner_id).first()
  comment.content = content
  db.commit()
  return JSONResponse(content={"message": "Operation successful"}, status_code=status.HTTP_200_OK)

@app.delete("/shanyraks/{id}/comments")
async def delete_comment(id: int, comment_id: int, token: str = Cookie()):
  db = SessionLocal()
  owner_id = decode_jwt(token)
  comment = db.query(models.Comment).filter(models.Comment.id == comment_id, models.Comment.house_id == id, models.Comment.author_id == owner_id).first()
  if comment:
    db.delete(comment)
    db.commit()
    return JSONResponse(content={"message": "Operation successful"}, status_code=status.HTTP_200_OK)
  else:

    raise HTTPException(status_code=404, detail="Item not found")
