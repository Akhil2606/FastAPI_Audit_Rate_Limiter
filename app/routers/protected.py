from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/protected",
    tags=["Protected"],
)


@router.get("/hello")
def protected_hello(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": f"Hello {current_user.username}",
        "user_id": current_user.id,
    }