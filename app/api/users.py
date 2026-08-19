"""API routes for User management."""
from fastapi import APIRouter
from app.schemas.response import APIResponseSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def list_users():
    return APIResponseSchema(success=True, message="User service ready", data=[])
