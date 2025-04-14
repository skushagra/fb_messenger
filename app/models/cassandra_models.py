"""
Models for interacting with Cassandra tables.
"""
import uuid
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set

from app.db.cassandra_client import cassandra_client

class MessageModel:
    """
    Message model for interacting with the messages table.
    
    Tables:
    - messages_by_conversation: stores messages in a conversation
    - user_conversations: stores user's conversations with recent activity
    """
    
    @staticmethod
    async def create_message(
        conversation_id: UUID, 
        sender_id: UUID, 
        message_text: str, 
        participant_ids: Optional[List[UUID]] = None
    ) -> UUID:
        """
        Create a new message and update user conversations.
        
        Args:
            conversation_id: The ID of the conversation
            sender_id: The ID of the message sender
            message_text: The content of the message
            participant_ids: List of participant IDs in the conversation
            
        Returns:
            The generated message ID
        """
        message_id = uuid.uuid4()
        message_timestamp = datetime.utcnow()
        
        try:
            # Insert the message into messages_by_conversation table
            insert_query = """
            INSERT INTO messages_by_conversation (
                conversation_id, message_timestamp, message_id, sender_id, message_text
            ) VALUES (%s, %s, %s, %s, %s)
            """
            cassandra_client.execute(insert_query, (
                conversation_id,
                message_timestamp,
                message_id,
                sender_id,
                message_text
            ))
            
            # If participant_ids not provided, default to just the sender
            if not participant_ids:
                participant_ids = [sender_id]
                
            # Update the user_conversations table for each participant
            for user_id in participant_ids:
                update_query = """
                INSERT INTO user_conversations (
                    user_id, last_activity, conversation_id, participant_ids, last_message_preview
                ) VALUES (%s, %s, %s, %s, %s)
                """
                last_message_preview = message_text[:100]
                cassandra_client.execute(update_query, (
                    user_id,
                    message_timestamp,
                    conversation_id,
                    set(participant_ids),
                    last_message_preview
                ))
                
            return message_id
        except Exception as e:
            raise Exception(f"Failed to create message: {str(e)}")
    
    @staticmethod
    async def get_conversation_messages(
        conversation_id: UUID, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get messages for a conversation with pagination.
        
        Args:
            conversation_id: The ID of the conversation
            page: The page number
            limit: Number of messages per page
            
        Returns:
            Tuple of (messages list, total count)
        """
        try:
            if page < 1:
                page = 1
                
            # First get the total count
            count_query = """
            SELECT COUNT(*) as count FROM messages_by_conversation
            WHERE conversation_id = %s
            """
            count_result = cassandra_client.execute(count_query, (conversation_id,))
            total = count_result[0]['count'] if count_result else 0
            
            # Then get the paginated results
            # Note: Cassandra doesn't directly support OFFSET, so for a real 
            # implementation we'd use token-based pagination
            select_query = """
            SELECT conversation_id, message_timestamp, message_id, sender_id, message_text
            FROM messages_by_conversation
            WHERE conversation_id = %s
            ORDER BY message_timestamp DESC
            LIMIT %s
            """
            rows = cassandra_client.execute(select_query, (conversation_id, limit))
            
            return list(rows), total
        except Exception as e:
            raise Exception(f"Failed to get conversation messages: {str(e)}")
    
    @staticmethod
    async def get_messages_before_timestamp(
        conversation_id: UUID, 
        before_timestamp: datetime,
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get messages before a timestamp with pagination.
        
        Args:
            conversation_id: The ID of the conversation
            before_timestamp: Get messages before this timestamp
            page: The page number
            limit: Number of messages per page
            
        Returns:
            Tuple of (messages list, total count)
        """
        try:
            if page < 1:
                page = 1
                
            # First get the total count
            count_query = """
            SELECT COUNT(*) as count FROM messages_by_conversation
            WHERE conversation_id = %s AND message_timestamp < %s
            """
            count_result = cassandra_client.execute(count_query, (
                conversation_id,
                before_timestamp
            ))
            total = count_result[0]['count'] if count_result else 0
            
            # Then get the paginated results
            select_query = """
            SELECT conversation_id, message_timestamp, message_id, sender_id, message_text
            FROM messages_by_conversation
            WHERE conversation_id = %s AND message_timestamp < %s
            ORDER BY message_timestamp DESC
            LIMIT %s
            """
            rows = cassandra_client.execute(select_query, (
                conversation_id,
                before_timestamp,
                limit
            ))
            
            return list(rows), total
        except Exception as e:
            raise Exception(f"Failed to get messages before timestamp: {str(e)}")


class ConversationModel:
    """
    Conversation model for interacting with the conversations-related tables.
    """
    
    @staticmethod
    async def get_user_conversations(
        user_id: UUID, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get conversations for a user with pagination.
        
        Args:
            user_id: The ID of the user
            page: The page number
            limit: Number of conversations per page
            
        Returns:
            Tuple of (conversations list, total count)
        """
        try:
            if page < 1:
                page = 1
                
            # First get the total count
            count_query = """
            SELECT COUNT(*) as count FROM user_conversations
            WHERE user_id = %s
            """
            count_result = cassandra_client.execute(count_query, (user_id,))
            total = count_result[0]['count'] if count_result else 0
            
            # Then get the paginated results
            select_query = """
            SELECT user_id, last_activity, conversation_id, participant_ids, last_message_preview
            FROM user_conversations
            WHERE user_id = %s
            ORDER BY last_activity DESC
            LIMIT %s
            """
            rows = cassandra_client.execute(select_query, (user_id, limit))
            
            return list(rows), total
        except Exception as e:
            raise Exception(f"Failed to get user conversations: {str(e)}")
    
    @staticmethod
    async def get_conversation(conversation_id: UUID) -> Dict[str, Any]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            Conversation details
        """
        try:
            query = """
            SELECT conversation_id, participant_ids
            FROM user_conversations
            WHERE conversation_id = %s
            LIMIT 1
            """
            result = cassandra_client.execute(query, (conversation_id,))
            
            if not result:
                raise Exception(f"Conversation {conversation_id} not found")
                
            return result[0]
        except Exception as e:
            raise Exception(f"Failed to get conversation: {str(e)}")
    
    @staticmethod
    async def create_or_get_conversation(
        user_id: UUID, 
        other_user_id: UUID
    ) -> Tuple[UUID, bool]:
        """
        Get an existing conversation between two users or create a new one.
        
        Args:
            user_id: The ID of the first user
            other_user_id: The ID of the second user
            
        Returns:
            Tuple of (conversation_id, was_created)
        """
        try:
            # Try to find existing conversation
            query = """
            SELECT conversation_id FROM user_conversations
            WHERE user_id = %s
            """
            result = cassandra_client.execute(query, (user_id,))
            
            # Iterate through conversations to find one with just these two participants
            for row in result:
                conv_id = row['conversation_id']
                # Get this conversation's details
                conv_details = await ConversationModel.get_conversation(conv_id)
                participants = conv_details['participant_ids']
                
                # If this conversation has exactly these two participants, return it
                if participants and len(participants) == 2 and user_id in participants and other_user_id in participants:
                    return conv_id, False
                    
            # If no matching conversation found, create a new one
            new_conversation_id = uuid.uuid4()
            participant_ids = [user_id, other_user_id]
            timestamp = datetime.utcnow()
            
            # Insert for both users
            for uid in participant_ids:
                query = """
                INSERT INTO user_conversations (
                    user_id, last_activity, conversation_id, participant_ids, last_message_preview
                ) VALUES (%s, %s, %s, %s, %s)
                """
                cassandra_client.execute(query, (
                    uid,
                    timestamp,
                    new_conversation_id,
                    set(participant_ids),
                    "New conversation"
                ))
                
            return new_conversation_id, True
        except Exception as e:
            raise Exception(f"Failed to create or get conversation: {str(e)}") 