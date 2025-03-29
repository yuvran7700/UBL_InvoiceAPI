# src/services/health_service.py

"""
Module responsible for tracking the readiness status of various subsystems in the application. 
Called by: health_check_routes.py
"""

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
