#src/validators/missing_field_checker.py

from typing import List
from pydantic import BaseModel
from src.domain.models.email_models import SendEmailModel, MissingEmailFieldsReport

class MissingEmailFieldChecker:
    def __init__(self, email: SendEmailModel):
        self.email = email

    MANDATORY_FIELDS = [
        "to_email",
        "subject",
        "file_name",
        "file_type"
    ]

    def run(self) -> MissingEmailFieldsReport:
        """
        Runs the missing field check and returns a structured report.
        """
        header_missing = self._find_missing_fields()
        return MissingEmailFieldsReport(
            missing_email_fields=header_missing,
        )

    def _find_missing_fields(self) -> List[str]:
        missing = []
        for field_path in self.MANDATORY_FIELDS:
            if not self._resolve_field(self.email, field_path):
                missing.append(field_path)
        return missing
    
    def _resolve_field(self, instance: BaseModel, field_path: str):
        current = instance
        for part in field_path.split("."):
            if isinstance(current, BaseModel):
                current = getattr(current, part, None)
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
