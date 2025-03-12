from fastapi import FastAPI
from src.routes.auth_routes import router as auth_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "UBL Invoice API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

app.include_router(auth_router)