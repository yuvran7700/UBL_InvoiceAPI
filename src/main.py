# This is the main file that will run the FastAPI application
from mangum import Mangum
from fastapi import FastAPI
from src.db.dynamodb_client import initialise_dynamodb
from src.services.health_service import HealthService


from src.routes.auth_routes import router as auth_router
from src.routes.user_routes import router as user_router
from src.routes.invoice_routes import router as invoice_router
from src.routes.health_check_routes import router as health_router


app = FastAPI()
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
