from typing import Optional, List
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status

from app.schemas.message import MessageCreate, MessageResponse, PaginatedMessageResponse
from app.models.cassandra_models import MessageModel

class MessageController:
    """
    Controller for handling message operations
    """
    
    async def send_message(self, message_data: MessageCreate) -> MessageResponse:
        """
        Send a message in a conversation
        
        Args:
            message_data: The message data including message_text, sender_id, and conversation_id
            
        Returns:
            The created message with metadata
        
        Raises:
            HTTPException: If message sending fails
        """
        try:
            message_id = await MessageModel.create_message(
                conversation_id=message_data.conversation_id,
                sender_id=message_data.sender_id,
                message_text=message_data.message_text,
                participant_ids=message_data.participant_ids if hasattr(message_data, 'participant_ids') else None
            )
            
            return MessageResponse(
                message_id=message_id,
                sender_id=message_data.sender_id,
                message_text=message_data.message_text,
                message_timestamp=datetime.utcnow(),
                conversation_id=message_data.conversation_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}"
            )
    
    async def get_conversation_messages(
        self, 
        conversation_id: UUID, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedMessageResponse:
        """
        Get all messages in a conversation with pagination
        
        Args:
            conversation_id: ID of the conversation
            page: Page number
            limit: Number of messages per page
            
        Returns:
            Paginated list of messages
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        try:
            messages, total = await MessageModel.get_conversation_messages(
                conversation_id=conversation_id,
                page=page,
                limit=limit
            )
            
            # Convert model data to schema response format
            message_responses = [
                MessageResponse(
                    message_id=msg['message_id'],
                    sender_id=msg['sender_id'],
                    message_text=msg['message_text'],
                    message_timestamp=msg['message_timestamp'],
                    conversation_id=msg['conversation_id']
                ) for msg in messages
            ]
            
            return PaginatedMessageResponse(
                total=total,
                page=page,
                limit=limit,
                data=message_responses
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversation messages: {str(e)}"
            )
    
    async def get_messages_before_timestamp(
        self, 
        conversation_id: UUID, 
        before_timestamp: datetime,
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedMessageResponse:
        """
        Get messages in a conversation before a specific timestamp with pagination
        
        Args:
            conversation_id: ID of the conversation
            before_timestamp: Get messages before this timestamp
            page: Page number
            limit: Number of messages per page
            
        Returns:
            Paginated list of messages
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        try:
            messages, total = await MessageModel.get_messages_before_timestamp(
                conversation_id=conversation_id,
                before_timestamp=before_timestamp,
                page=page,
                limit=limit
            )
            
            # Convert model data to schema response format
            message_responses = [
                MessageResponse(
                    message_id=msg['message_id'],
                    sender_id=msg['sender_id'],
                    message_text=msg['message_text'],
                    message_timestamp=msg['message_timestamp'],
                    conversation_id=msg['conversation_id']
                ) for msg in messages
            ]
            
            return PaginatedMessageResponse(
                total=total,
                page=page,
                limit=limit,
                data=message_responses
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get messages before timestamp: {str(e)}"
            ) 