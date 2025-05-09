from fastapi import APIRouter
from typing import Union
from enum import Enum
from .test_db import items_db
from pydantic import BaseModel


router = APIRouter(tags=["Items"])


@router.get("/")
async def home():
    return {"message": "This is homepage"}


@router.get("/items")
async def get_items() -> list:
    return items_db


@router.get("/items/{item_id}")
async def get_item(item_id: int) -> Union[dict[str, str] | None]:
    item = next((item for item in items_db if item["id"] == item_id), None)
    if item:
        return item

    return {"message": f"No Item found with id {item_id}"}


class StatusChoices(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@router.get("/items/{status}")
async def get_orders(status: StatusChoices):
    if status is StatusChoices.PENDING:
        return {"message": "No items"}

    if status is StatusChoices.REJECTED:
        return {"total": 100}

    if status is StatusChoices.APPROVED:
        return {"total": 1000}


# Implementing Pagination using query parameters

# You can declare multiple path parameters and query parameters at the same time, FastAPI knows which is which.
# And you don't have to declare them in any specific order.


@router.get("/paginated-items/users/{user_id}")
async def get_paginated_items(user_id: int, offset: int = 0, limit: int = 10):
    filtered = [item for item in items_db if item["created_by"] == user_id]
    return filtered[offset : offset + limit]


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@router.post("/items")
async def create_item(item: Item):
    return item


"""
If the parameter is also declared in the path, it will be used as a path parameter.
If the parameter is of a singular type (like int, float, str, bool, etc) it will be interpreted as a query parameter.
If the parameter is declared to be of the type of a Pydantic model, it will be interpreted as a request body.
"""


@router.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    item = dict(item)
    item["q"] = q
    return item
