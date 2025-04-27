# src/services/health_service.py

"""
Module responsible for tracking the readiness status of various subsystems in the application. 
Called by: health_check_routes.py
"""
import httpx

class HealthService:
    """
    It allows setting the readiness state of individual subsystems and 
    retrieving the overall system status.
    """
    def __init__(self):
        """
        Initializes the HealthService with default readiness states for subsystems.
        """
        self._subsystems_ready = {
            "dynamo.users": False,
            "dynamo.invoices": False,
            "dynamo.sessions": False,
            "external_ready": True  # Defaulted to true unless integrated later
        }
        self._external_services_health = {
            "propelauth": False  # Default False until checked
        }
        self.auth_url = "https://39356306333.propelauthtest.com"

    def set_ready(self, key: str, value: bool = True):
        """
        Sets the readiness state of a specific subsystem.

        Args:
            key (str): The name of the subsystem to update.
            value (bool): The readiness state to set (default is True).
        """
        if key in self._subsystems_ready:
            self._subsystems_ready[key] = value

    def is_ready(self) -> bool:
        """
        Checks if all subsystems are ready.

        Returns:
            bool: True if all subsystems are ready, False otherwise.
        """
        return all(self._subsystems_ready.values())

    def get_status(self) -> dict:
        """
        Retrieves the overall readiness status and details of all subsystems.

        Returns:
            dict: A dictionary containing the overall status ("ready" or "not_ready") 
                  and the readiness details of each subsystem.
        """
        return {
            "status": "ready" if self.is_ready() else "not_ready",
            "details": self._subsystems_ready.copy() 
        }
    
    async def check_external_services(self):
        """
        Asynchronously pings external services like PropelAuth.
        """
        async with httpx.AsyncClient(timeout=3) as client:
            try:
                response = await client.get(f"{self.auth_url}/health")
                self._external_services_health["propelauth"] = response.status_code == 200
            except Exception:
                self._external_services_health["propelauth"] = False
