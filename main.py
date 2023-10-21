from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from pymongo import MongoClient
from typing import Optional
from bson import ObjectId

app = FastAPI()

mongo_client = MongoClient(
    "mongodb+srv://myMac:clothingApp@cluster0.l19f373.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client["api-workshop"]
orders_collection = db["orders"]


class Order(BaseModel):
    order_number: Optional[str]
    table_number: Optional[int]
    order_items: Optional[list]
    order_status: Optional[str]


@app.get("/order/open")
async def get_open_orders():

    open_orders = list(orders_collection.find({"order_status": "open"}))
    orders = [dict(order, _id=str(order['_id'])) for order in open_orders]
    return orders


@app.post("/order")
async def create_order(order: Order):
    result = orders_collection.insert_one(order.dict())
    if result.inserted_id:
        return {"message": "Order created successfully", "order_id": str(result.inserted_id)}
    else:
        raise HTTPException(
            status_code=500, detail="Failed to create the order")


@app.put("/order/{order_id}")
async def update_order(order_id: str, order: Order):

    existing_order = orders_collection.find_one({"_id": ObjectId(order_id)})

    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")

    update_data = order.dict(exclude_unset=True)
    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)}, {"$set": update_data})

    if result.modified_count > 0:
        return {"message": "Order updated successfully"}
    else:
        raise HTTPException(
            status_code=500, detail="Failed to update the order")


@app.delete("/order/{order_id}")
async def delete_order(order_id: str):

    existing_order = orders_collection.find_one({"_id": ObjectId(order_id)})

    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if existing_order["order_status"] != "Open":
        raise HTTPException(
            status_code=400, detail="Order status is not 'Open'. Cannot delete.")

    result = orders_collection.delete_one({"_id": ObjectId(order_id)})

    if result.deleted_count == 1:
        return {"message": "Order deleted successfully"}
    else:
        raise HTTPException(
            status_code=500, detail="Failed to delete the order")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
