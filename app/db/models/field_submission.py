from sqlalchemy import Column, Float, String, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class FieldStatus(str, enum.Enum):
    DRAFT = "draft"
    FINAL = "final"
    PENDING = "pending"

class FieldSubmission(Base):
    """
    Represents the "submission" of a specific field.
    This submission is linked to a FieldTemplate (definition
    of the field, a description, etc.) and a Form (the 
    overall form being filled out during a conversation). 

    A couple of notes:
    - The "status" attribute indicates whether the field
      has ben filled out, whether it's a draft (i.e., the agent
      determines it needs more info), or whether it's final.
    - The "value" attribute holds the actual content submitted
      for this field. For now, it's a simple string containing
      the latest value. May expand to more complex structures later.
    """

    __tablename__ = "field_submissions"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=True)
    status = Column(Enum(FieldStatus), nullable=False)
    llm_confidence = Column(Float, nullable=True)  # Confidence score from LLM (0-100)

    # ----Timestamps----
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # ----Foreign Keys----
    form_id = Column(Integer, ForeignKey("forms.id"))
    field_template_id = Column(Integer, ForeignKey("field_templates.id"))

    # ----Relationships----
    form = relationship("Form", back_populates="field_submissions")
    field_template = relationship("FieldTemplate", back_populates="field_submissions")