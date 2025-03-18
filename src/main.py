"""Adding routes for API usage"""
from fastapi import FastAPI
from src.routes.auth_routes import router as auth_router  # Adjust import as neede
from src.routes.user_routes import router as user_router
app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
def read_root():
    """Ensuring API is running"""
    return {"message": "UBL Invoice API is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
