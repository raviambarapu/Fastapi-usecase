from fastapi import APIRouter, Depends

from app.dependencies import require_permission
from app.models.user import User
from app.permissions import Permission

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.post("/products")
def create_product(current_user: User = Depends(require_permission(Permission.PRODUCT_WRITE))):
    return {"message":"Product created", "created_by":current_user.email}


@router.delete("/products/{product_id}")
def delete_product(product_id: int,current_user: User = Depends(require_permission(Permission.PRODUCT_DELETE))):
    return {"message":f"Product {product_id} deleted","deleted_by":current_user.email}