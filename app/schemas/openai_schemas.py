from pydantic import BaseModel
from enum import Enum

class DefaultLLMOutput(BaseModel):
    output_text: str



class FieldUpdateType(str, Enum):
    CREATE = "create"
    UPDATE = "update"

class FieldToUpdate(BaseModel):
    type: FieldUpdateType  # "create" | "update"
    template_field_id: str
    field_name: str
    new_value: str
    confidence: float
    reasoning: str

class UpdateFormLLMOutput(BaseModel):
    fields_to_update: list[FieldToUpdate]  # Each dict contains details about the field to update