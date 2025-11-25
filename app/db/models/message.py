from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(Enum("user", "agent", "system", name="sender_enum"), nullable=False)
    
    # TO DO - make sure this is best method for step key
    message_num = Column(Integer, nullable=False)

    
    # TO DO - how are we integrating PDFs or TXT files into this?
    content = Column(String, nullable=False)

    # ----Timestamps----
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ----Foreign Keys----
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # ----Relationships----
    conversation = relationship("Conversation", back_populates="messages")
    owner = relationship("User", back_populates="messages")


