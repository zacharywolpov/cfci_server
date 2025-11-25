from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base



class Conversation(Base):
    """
    Represents conversation between user and AI agent.
    
    Each conversation linked to:
    - A user (the owner of the conversation)
    - A form (the form being filled out during the conversation)
        - THROUGH the form, we can access the 
    - Many messages
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # ----Foreign Keys----
    user_id = Column(Integer, ForeignKey("users.id"))
    form_id = Column(Integer, ForeignKey("forms.id"))

    # ----Relationships----

    # One-to-many relationship with Message
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    # One-to-one relationship with Form
    # Question - delete the associated form when this conv is deleted??
    form = relationship("Form", back_populates="conversation")

    # Many-to-one relationship with user
    owner = relationship("User", back_populates="conversations")