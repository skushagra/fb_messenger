from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.controllers.conversation_controller import ConversationController
from app.schemas.conversation import ConversationResponse, PaginatedConversationResponse

router = APIRouter()

@router.get("/api/conversations/user/{user_id}", response_model=PaginatedConversationResponse)
async def get_conversations_for_user(
    user_id: UUID,
    page: int = 1,
    limit: int = 20,
    conversation_controller: ConversationController = Depends()
):
    """
    Get all conversations for a given user, ordered by most recent activity (DESC).
    """
    try:
        return await conversation_controller.get_user_conversations(
            user_id=user_id,
            page=page,
            limit=limit
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversations: {str(e)}"
        )

@router.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    conversation_controller: ConversationController = Depends()
):
    """
    Get details of a specific conversation by ID
    """
    try:
        return await conversation_controller.get_conversation(conversation_id=conversation_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation: {str(e)}"
        )
