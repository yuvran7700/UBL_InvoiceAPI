# This is the main file that will run the FastAPI application
from mangum import Mangum
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI
from src.db.dynamodb_client import initialise_dynamodb
from src.services.health_service import HealthService
from src.swagger_config import tags_metadata

# FastAPI routes imports
from src.routes.auth_routes import router as auth_router
from src.routes.user_routes import router as user_router
from src.routes.invoice_routes import router as invoice_router
from src.routes.health_check_routes import router as health_router

# Custom exception and eror handler imports
from src.exceptions.base_exceptions import APIBaseException
from src.exceptions.error_handler import (
    api_base_exception_handler,
    request_validation_exception_handler,
    generic_exception_handler,
)


app = FastAPI(
    title="UBL Invoice API",
    description = (
    "UBL Invoice API for handling invoice operations and secure authentication.\n\n"
        "**Testing Instructions**\n\n"
        "To test any secured route easily:\n"
        "1. Click the **Authorize** button at the top right of this Swagger UI.\n"
        "2. Paste this token into the popup field: **test-token**\n"
        "3. Click **Authorize**, then use any protected endpoint.\n\n"
        "Supports uploading, completing, and downloading UBL invoices in XML/JSON.\n"
        "Includes JWT-based login, logout, and session validation."
    ),
    version="1.0.0",
    docs_url="/docs",  # Swagger UI path
    redoc_url="/redoc",  # ReDoc path (can be None to disable)
    swagger_ui_parameters={
        "docExpansion": "none",
        "defaultModelsExpandDepth": 1,
        "displayRequestDuration": True,
        "filter": True,
    },
    openapi_tags=tags_metadata,
)

app.add_exception_handler(APIBaseException, api_base_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.state.health_service = HealthService()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(invoice_router)
app.include_router(health_router)


@app.on_event("startup")
async def startup_tasks():
    """
    initializes the DynamoDB client and sets up the health service 
    to monitor the readiness of the application subsystems.
    """
    initialise_dynamodb(app.state.health_service)


@app.get("/")
def read_root():
    """Ensuring API is running"""
    return {"message": "UBL Invoice API is running!"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

handler = Mangum(app)
