# src/testing_main.py

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

# Only include the specific v2 routes you want to test
from src.routes.invoice_routes_v2 import router as invoice_router_v2
from src.routes.email_routes import router as email_router
from src.routes.order_routes import router as order_router
# Import your custom exception handling setup
from src.exceptions.base_exceptions import APIBaseException
from src.exceptions.error_handler import (
    api_base_exception_handler,
    request_validation_exception_handler,
    generic_exception_handler,
)

# Minimal app for testing only
app = FastAPI(title="UBL Invoice API (Testing)")

# Register exception handlers (copied from main.py)
app.add_exception_handler(APIBaseException, api_base_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Only mount v2 invoice routes for now
app.include_router(invoice_router_v2)
app.include_router(email_router)
app.include_router(order_router)

@app.get("/")
def read_root():
    return {"message": "UBL Invoice API Testing App Running!"}
