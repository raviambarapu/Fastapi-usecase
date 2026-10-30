from fastapi import APIRouter

router = APIRouter(tags=["Products version 02"])

@router.get("/products")
def product_v2():

    return {
        "version":2,
        "items":[
            {
                "id":1,
                "name":"Laptop"
            },
            {
                "id":2,
                "name":"Mouse"
            }
        ],
        "total":2
    }