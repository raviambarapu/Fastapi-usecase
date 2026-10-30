from enum import StrEnum

class Permission(StrEnum):
    PRODUCT_READ = "products:read"
    PRODUCT_WRITE = "products:write"
    PRODUCT_DELETE = "products:delete"

    ORDERS_READ = "oders:read"
    ORDERS_WRITE = "orders:write"

    USERS_MANAGE = "users:manage"

ROLE_PERMISSION: dict[str, set[str]] = {

    "admin":{
        Permission.PRODUCT_READ,
        Permission.PRODUCT_WRITE,
        Permission.PRODUCT_DELETE,
        Permission.ORDERS_READ,
        Permission.ORDERS_WRITE,
        Permission.USERS_MANAGE,
    },

    "manager":{
        Permission.PRODUCT_READ,
        Permission.PRODUCT_WRITE,
        Permission.ORDERS_READ,
        Permission.ORDERS_WRITE,
    },

    "viewer":{
        Permission.PRODUCT_READ,
        Permission.ORDERS_READ,
    }
}

def get_permissions(role:str) -> set[str]:
    return ROLE_PERMISSION(role,set())