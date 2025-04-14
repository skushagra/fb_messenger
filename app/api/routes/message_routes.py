from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.controllers.message_controller import MessageController
from app.schemas.message import MessageCreate, MessageResponse, PaginatedMessageResponse

router = APIRouter()

@router.post("/api/messages/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    message_controller: MessageController = Depends()
):
    """
    Send a message in a conversation. Also updates the user_conversations table 
    for each participant.
    """
    try:
        return await message_controller.send_message(message_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )

@router.get("/api/messages/conversation/{conversation_id}", response_model=PaginatedMessageResponse)
async def get_messages_in_conversation(
    conversation_id: UUID,
    page: int = 1,
    limit: int = 20,
    message_controller: MessageController = Depends()
):
    """
    Retrieves messages in a conversation with pagination.
    Ordered by message_timestamp DESC from Cassandra schema.
    """
    try:
        return await message_controller.get_conversation_messages(
            conversation_id=conversation_id,
            page=page,
            limit=limit
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        )

@router.get("/api/messages/conversation/{conversation_id}/before", response_model=PaginatedMessageResponse)
async def get_messages_before_timestamp(
    conversation_id: UUID,
    timestamp: datetime,
    page: int = 1,
    limit: int = 20,
    message_controller: MessageController = Depends()
):
    """
    Retrieves messages before a given timestamp with pagination.
    """
    try:
        return await message_controller.get_messages_before_timestamp(
            conversation_id=conversation_id,
            before_timestamp=timestamp,
            page=page,
            limit=limit
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        )
