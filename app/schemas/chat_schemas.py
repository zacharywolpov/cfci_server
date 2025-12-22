from pydantic import BaseModel

class InitiateChatResponse(BaseModel):
    conversation_id: int
    form_id: int

class AdvanceChatRequest(BaseModel):
    conversation_id: int
    user_message: str
    message_step_num: int

class AdvanceChatResponse(BaseModel):
    message_id: int
    message_num: int
    sender: str
    content: str