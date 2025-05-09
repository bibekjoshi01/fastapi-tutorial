from fastapi import APIRouter, Query, Path, Body
from typing import Annotated
from pydantic import AfterValidator, BaseModel

from .test_db import users_db


router = APIRouter(prefix="/users", tags=["Users"])


def email_validator(email: str):
    if not "@" in email:
        raise ValueError("Invalid email")

    return email


@router.get("")
async def list_users(
    q: Annotated[list[str] | None, Query(min_length=3, max_length=50)] = None,
    email: Annotated[str | None, AfterValidator(email_validator)] = None,
):
    """Example: /users?q=param1&q=param2&q=param3"""

    results = users_db

    if email:
        results = [user for user in users_db if user["email"] == email]

    return results


@router.get("/{user_id}")
async def retrieve_user(user_id: Annotated[int, Path(title="ID of the user", gt=0)]):
    result = next((user for user in users_db if user["id"] == user_id), None)
    if result:
        return result

    return {"error": "User not found!"}


class User(BaseModel):
    name: str
    email: str


@router.post("")
async def create_user(user: User):
    user = dict(user)
    print(user, "user data")
    new_user = {
        "id": users_db[-1]["id"] + 1,
        "name": user["name"],
        "email": user["email"],
        "is_active": True,
    }
    
    return {"message": "success", "data": new_user}
