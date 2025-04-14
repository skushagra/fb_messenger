from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status

from app.schemas.conversation import ConversationResponse, PaginatedConversationResponse
from app.models.cassandra_models import ConversationModel

class ConversationController:
    """
    Controller for handling conversation operations
    """
    
    async def get_user_conversations(
        self, 
        user_id: UUID, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedConversationResponse:
        """
        Get all conversations for a user with pagination
        
        Args:
            user_id: ID of the user
            page: Page number
            limit: Number of conversations per page
            
        Returns:
            Paginated list of conversations
            
        Raises:
            HTTPException: If user not found or access denied
        """
        try:
            conversations, total = await ConversationModel.get_user_conversations(
                user_id=user_id,
                page=page,
                limit=limit
            )
            
            # Convert model data to schema response format
            conversation_responses = [
                ConversationResponse(
                    conversation_id=conv['conversation_id'],
                    user_id=conv['user_id'],
                    participant_ids=list(conv['participant_ids']) if conv['participant_ids'] else [],
                    last_activity=conv['last_activity'],
                    last_message_preview=conv['last_message_preview']
                ) for conv in conversations
            ]
            
            return PaginatedConversationResponse(
                total=total,
                page=page,
                limit=limit,
                data=conversation_responses
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user conversations: {str(e)}"
            )
    
    async def get_conversation(self, conversation_id: UUID) -> ConversationResponse:
        """
        Get a specific conversation by ID
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation details
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        try:
            conversation = await ConversationModel.get_conversation(conversation_id=conversation_id)
            
            # Since we don't have user_id in this query, we'll use the first participant as the user
            user_id = list(conversation['participant_ids'])[0] if conversation['participant_ids'] else None
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation has no participants"
                )
                
            return ConversationResponse(
                conversation_id=conversation['conversation_id'],
                user_id=user_id,
                participant_ids=list(conversation['participant_ids']),
                last_activity=datetime.utcnow(),  # Placeholder as this isn't in our query
                last_message_preview=""  # Placeholder as this isn't in our query
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversation: {str(e)}"
            ) 