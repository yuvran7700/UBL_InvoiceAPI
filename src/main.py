from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import user_routes

app = FastAPI(
    title="User API",
    description="API for managing users with DynamoDB",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the User API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)