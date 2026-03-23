# Sample FastAPI app for testing
from fastapi import FastAPI, APIRouter

app = FastAPI(title="Test API")

router = APIRouter()

@app.get("/")
def root():
    return {"msg": "Hello"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

app.include_router(router)

@router.post("/items/{item_id}")
def create_item(item_id: str):
    pass
