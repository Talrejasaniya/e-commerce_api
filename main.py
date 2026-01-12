from fastapi import FastAPI,Depends,HTTPException, Response,status
from pydantic import BaseModel
from database import engine,Base,SessionLocal
from utils import hash_password,verify_password, create_access_token
from sqlalchemy.orm import Session
import models,utils,schemas
from sqlalchemy.exc import IntegrityError

models.Base.metadata.create_all(bind=engine)
app=FastAPI()


class Product(BaseModel):
    name: str
    price: int
    is_sale: bool =False
    inventory: int=10



# Dependency (Ye har request par DB session banayega aur baad me band karega)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    # SQL Query: SELECT * FROM products;
    products = db.query(models.ProductDB).all()
    return products

@app.post("/products")
def add_product(item:Product,db: Session = Depends(get_db)):
    new_product=models.ProductDB(
        name=item.name,
        price=item.price,
        is_sale=item.is_sale,
        inventory=item.inventory
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


    
@app.delete("/products/{id}")
def delete_product(id:int,db:Session=Depends(get_db)):
    #first find the product existing in DB
    product=db.query(models.ProductDB).filter(models.ProductDB.id==id).first()
    
    # product does not exist,return none and error message
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    
    # product exists,delete it from DB 
    db.delete(product)
    #final save commit
    db.commit()
    #return deleted product message
    return{"message":"product deleted successfully"}

@app.put("/products/{product_id}")
def update_product(product_id:int,item:Product,db:Session=Depends(get_db)):
    product_query=db.query(models.ProductDB).filter(models.ProductDB.id==product_id)
    product=product_query.first()
    
     
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    
    product_query.update(item.dict(),synchronize_session=False)
    
    db.commit()
    
    return product_query.first()

#signup endpoint
@app.post("/users",status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate,db:Session=Depends(get_db)):
    hashed_pwd=utils.hash_password(user.password)
    user.password=hashed_pwd
    new_user=models.User(**user.dict())
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered")
    
    return new_user

@app.post("/login")
def login(user_credentials:schemas.UserLogin,db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.email==user_credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
        
    if not utils.verify_password(user_credentials.password,user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    
    access_token = create_access_token(data={"user_id": user.id})   
    return {"access_token": access_token, "token_type": "bearer"}
    