from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Form(Base):
    """
    Represents the "form" that is being ultimately filled
    out by the AI agent as a conversation moves along.
    
    Represents an AI-generated version of the form currently
    used by the CFCI team, where intake clients fill 
    the form out to get in contact with CFCI.
    """
    __tablename__ = "forms"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)

    # ----Foreign Keys----
    user_id = Column(Integer, ForeignKey("users.id"))
    form_template_id = Column(Integer, ForeignKey("form_templates.id"))

    # ----Timestamps----
    # Form is "published" when it's sent to CFCI.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), server_default=func.now())

    # ----Relationships----
    conversation = relationship("Conversation", back_populates="form")
    field_templates = relationship("FieldTemplate", back_populates="form")
    field_submissions = relationship("FieldSubmission", back_populates="form", cascade="all, delete-orphan")
    form_template = relationship("FormTemplate", back_populates="forms")
    owner = relationship("User", back_populates="forms")