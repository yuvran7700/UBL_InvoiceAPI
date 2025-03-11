"""
Main entry point for the FastAPI application.
Initializes the app and includes API routes.
"""

from fastapi import FastAPI
from src.routes.order_routes import router as order_upload_router

app = FastAPI()

# Include the order upload routes under the '/v1/admin/order' prefix.
app.include_router(order_upload_router, prefix="/v1/admin/order")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
