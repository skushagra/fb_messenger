from pydantic import BaseModel, Field
from typing import List, Optional, Set
from datetime import datetime
from uuid import UUID
from app.schemas.message import MessageResponse

class ConversationResponse(BaseModel):
    conversation_id: UUID = Field(..., description="Unique ID of the conversation")
    user_id: UUID = Field(..., description="ID of the user viewing the conversation")
    participant_ids: List[UUID] = Field(..., description="List of all participants in the conversation")
    last_activity: datetime = Field(..., description="Timestamp of the last message")
    last_message_preview: Optional[str] = Field(None, description="Preview of the last message")

class ConversationDetail(ConversationResponse):
    messages: List[MessageResponse] = Field(..., description="List of messages in conversation")

class PaginatedConversationRequest(BaseModel):
    page: int = Field(1, description="Page number for pagination")
    limit: int = Field(20, description="Number of items per page")

class PaginatedConversationResponse(BaseModel):
    total: int = Field(..., description="Total number of conversations")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    data: List[ConversationResponse] = Field(..., description="List of conversations") 