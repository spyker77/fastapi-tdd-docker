from fastapi import APIRouter

router = APIRouter()


@router.get("/", include_in_schema=False)
async def home_page_message():
    return {"message": "Please refer to the /docs or /redoc path to access the API documentation"}
