"""
Script to generate test data for the Messenger application.
"""
import os
import uuid
import logging
import random
from datetime import datetime, timedelta
from cassandra.cluster import Cluster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cassandra connection settings
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "localhost")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "messenger_app")

# Test data configuration
NUM_USERS = 10  # Number of users to create
NUM_CONVERSATIONS = 15  # Number of conversations to create
MAX_MESSAGES_PER_CONVERSATION = 20  # Maximum number of messages per conversation

def connect_to_cassandra():
    """Connect to Cassandra cluster."""
    logger.info("Connecting to Cassandra...")
    try:
        cluster = Cluster([CASSANDRA_HOST])
        session = cluster.connect(CASSANDRA_KEYSPACE)
        logger.info("Connected to Cassandra!")
        return cluster, session
    except Exception as e:
        logger.error(f"Failed to connect to Cassandra: {str(e)}")
        raise

def generate_test_data(session):
    """Generate test data for the messenger application."""
    logger.info("Generating test data...")
    
    # Generate user IDs
    user_ids = [uuid.uuid4() for _ in range(NUM_USERS)]
    logger.info(f"Generated {len(user_ids)} users")
    
    # Log the user IDs for future reference
    for i, uid in enumerate(user_ids):
        logger.info(f"User {i+1}: {uid}")
    
    conversations = []
    # Create conversations
    for _ in range(NUM_CONVERSATIONS):
        # Select 2-4 random participants
        num_participants = random.randint(2, min(4, NUM_USERS))
        participants = random.sample(user_ids, num_participants)
        conversation_id = uuid.uuid4()
        conversations.append((conversation_id, participants))
        
        # Log the conversation details
        logger.info(f"Conversation {conversation_id} with participants: {participants}")
        
        # Generate messages for this conversation
        num_messages = random.randint(5, MAX_MESSAGES_PER_CONVERSATION)
        
        # Base timestamp for this conversation (between 1-30 days ago)
        start_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        for msg_idx in range(num_messages):
            # Each message is 1-30 minutes after the previous one
            message_timestamp = start_time + timedelta(minutes=msg_idx * random.randint(1, 30))
            
            # Select a random sender from participants
            sender_id = random.choice(participants)
            
            # Generate a message
            message_id = uuid.uuid4()
            message_text = f"Test message {msg_idx+1} in conversation {conversation_id}"
            
            # Insert message into messages_by_conversation
            insert_message_query = """
            INSERT INTO messages_by_conversation (
                conversation_id, message_timestamp, message_id, sender_id, message_text
            ) VALUES (%s, %s, %s, %s, %s)
            """
            session.execute(insert_message_query, (
                conversation_id,
                message_timestamp,
                message_id,
                sender_id,
                message_text
            ))
            
            # For the last message, update user_conversations for each participant
            if msg_idx == num_messages - 1:
                for user_id in participants:
                    upsert_conversation_query = """
                    INSERT INTO user_conversations (
                        user_id, last_activity, conversation_id, participant_ids, last_message_preview
                    ) VALUES (%s, %s, %s, %s, %s)
                    """
                    session.execute(upsert_conversation_query, (
                        user_id,
                        message_timestamp,
                        conversation_id,
                        set(participants),
                        message_text[:100]
                    ))
    
    logger.info(f"Generated {NUM_CONVERSATIONS} conversations with {MAX_MESSAGES_PER_CONVERSATION} messages each")
    logger.info("User IDs have been logged above for testing API endpoints")

def main():
    """Main function to generate test data."""
    cluster = None
    
    try:
        # Connect to Cassandra
        cluster, session = connect_to_cassandra()
        
        # Generate test data
        generate_test_data(session)
        
        logger.info("Test data generation completed successfully!")
    except Exception as e:
        logger.error(f"Error generating test data: {str(e)}")
    finally:
        if cluster:
            cluster.shutdown()
            logger.info("Cassandra connection closed")

if __name__ == "__main__":
    main()