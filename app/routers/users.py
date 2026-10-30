from fastapi import APIRouter, Depends, status
from app.dependencies import require_admin, require_role, get_current_user
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: User = Depends(require_role("admin"))):
    return None

@router.get("/admin-area")
def admin_area(current_user:User = Depends(require_role("admin"))):
    return{"message":"Welcome to admin area", "user": current_user.email}

@router.get("/management")
def management_area(current_user:User = Depends(require_role("admin","manager"))):
    return{"message":"Welcome to management area","user":current_user.email,"role":current_user.role}

@router.get("/profile")
def profile(current_user:User = Depends(get_current_user)):
    return current_user