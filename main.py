from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel
from database import engine,Base,SessionLocal
import models
from sqlalchemy.orm import Session

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