from typing import Dict, Any
from pydantic import ValidationError
from .schemas import SCHEMAS
from .exceptions import ValidationException


class Validator:
    def validate(self, data: Dict[str, Any], schema: str) -> Dict[str, Any]:
        if schema not in SCHEMAS:
            raise ValueError(f"Validation schema '{schema}' not defined")

        try:
            validated = SCHEMAS[schema](**data)
            return validated.model_dump(mode='json')  # Converts Decimals to floats
        except ValidationError as e:
            # Convert Pydantic errors to field:message dict like PHP
            messages = {}
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                messages[field] = error["msg"]
            raise ValidationException("Validation failed", messages)