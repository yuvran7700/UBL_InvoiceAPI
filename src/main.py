# This is the main file that will run the FastAPI application
from mangum import Mangum
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.dynamodb_client import initialise_dynamodb
from src.services.health_service import HealthService
from src.swagger_config import tags_metadata

# FastAPI v1 routes imports
from src.routes.v1.auth_routes import router as auth_router
from src.routes.v1.user_routes import router as user_router
from src.routes.health_check_routes import router as health_router


# FastAPI v2 routes imports
from src.routes.invoice_routes_v2 import router as invoice_router_v2
from src.routes.user_routes_v2 import router as user_router_v2
from src.routes.organisation_routes import router as organisation_router
from src.propelapi_test_helper import test_router as test_router
from src.routes.email_routes import router as email_route
from src.routes.order_routes import router as order_route

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
    "**Option 1: Create Your Own User and Organisation**\n"
    "- Visit the frontend signup page here: [Create Account](https://yourfrontendlink.com/signup)\n"
    "- After signing up, on the Dashboard/Home page:\n"
    "  - Scroll down to find the **'Your Profile'** card.\n"
    "  - Copy your **User ID** (it appears like `@ExampleUserId`). Copy it **without the @** symbol.\n"
    "  - Next, find the **'Your Organisations'** card next to it.\n"
    "  - Copy the **Organisation ID** listed there.\n"
    "- Then, paste both the User ID and Organisation ID into the **Testing Utilities** section to generate your access token.\n\n"
    "**Option 2: Use Pre-Existing Test Credentials**\n"
    "- Use the following provided IDs for quick testing:\n"
    "    - `user_id`: `ac5b71f7-f6f1-422c-9b47-f5ac9cbb81ed`\n"
    "    - `org_id`: `7303f5fd-063b-41bc-85ae-cc21b3676688`\n"
    "- Generate a token using these IDs from the **Testing Utilities** section.\n\n"
    "**Once You Have a Token:**\n"
    "1. Click the **Authorize** button at the top right of Swagger UI.\n"
    "2. Paste the generated token into the popup field.\n"
    "3. Click **Authorize**, and you can now access all protected endpoints.\n\n"
    "Supports uploading, completing, and downloading UBL invoices in XML/JSON.\n"
    "Includes JWT-based login, logout, and session validation."
    ),
    version="1.0.0",
    docs_url="/docs",  # Swagger UI path
    redoc_url="/redoc",  # ReDoc path (can be None to disable)
    root_path="",
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.health_service = HealthService()

# Registering v1 routers 
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(health_router)


# Registering v2 routers
app.include_router(user_router_v2)
app.include_router(invoice_router_v2)
app.include_router(organisation_router)
app.include_router(test_router)
app.include_router(email_route)
app.include_router(order_route)

@app.on_event("startup")
async def startup_tasks():
    """
    initializes the DynamoDB client and sets up the health service 
    to monitor the readiness of the application subsystems.
    """
    initialise_dynamodb(app.state.health_service)


@app.get("/", tags=["Testing Utilities (Internal Only)"])
def read_root():
    """Ensuring API is running"""
    return {"message": "UBL Invoice API is running!"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

handler = Mangum(app)
