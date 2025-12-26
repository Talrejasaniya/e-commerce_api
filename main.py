from fastapi import FastAPI,Depends
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
    
    

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    if product_id < 0 or product_id >= len(inventory):
        return {"error": "product not found"}
    removed_item=inventory.pop(product_id)
    return {"message": "product deleted successfully","deleted_item": removed_item}

