from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()

inventory=[]

class Product(BaseModel):
    name: str
    price: int
    description: str= None

@app.get("/products")
def get_products():
    return {"all_products": inventory}

@app.post("/products")
def add_product(product: Product):
    new_item=product.dict()
    inventory.append(new_item)
    return {"message":"Product add successfully","data": new_item}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    if product_id < 0 or product_id >= len(inventory):
        return {"error": "product not found"}
    removed_item=inventory.pop(product_id)
    return {"message": "product deleted successfully","deleted_item": removed_item}
