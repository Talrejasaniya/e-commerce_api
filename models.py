from sqlalchemy import Column,Integer, String ,Boolean
from database import Base

class ProductDB(Base):
    __tablename__="products"
    
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,index=True)
    price=Column(Integer)
    is_sale=Column(Boolean,default=False)
    inventory=Column(Integer,default=10)
    
class User(Base):
    __tablename__="users"
    
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,index=True)
    password=Column(String)