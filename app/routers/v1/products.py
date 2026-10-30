from fastapi import APIRouter

router = APIRouter(tags=["Products version 01"])

@router.get("/products")
def product_v1():

    return {
        "version":1,
        "items":[
            {
                "id":1,
                "name":"Laptop"
            },
            {
                "id":2,
                "name":"Mouse"
            }
        ]
    }