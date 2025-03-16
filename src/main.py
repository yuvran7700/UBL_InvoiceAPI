from fastapi import FastAPI
from routes.auth_routes import router as auth_router  # Adjust import as neede

app = FastAPI()

app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "UBL Invoice API is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
