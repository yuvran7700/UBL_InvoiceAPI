from fastapi import FastAPI
from routes.invoice_routes import router as invoice_router
from routes.user_routes import router as user_router
from db.dynamodb_client import initialize_dynamodb
from routes.order_routes import router as order_router

# Initialize FastAPI app
app = FastAPI(title="UBL Invoice API")

# Connect to DynamoDB
initialize_dynamodb()

# Include routers
app.include_router(order_router)
app.include_router(invoice_router)
app.include_router(user_router)

# Root endpoint (for testing if API is running)
@app.get("/")
async def root():
    return {"message": "UBL Invoice API is running!"}