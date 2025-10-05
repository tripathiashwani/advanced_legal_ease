import json
import logging
import threading
from typing import Dict
from confluent_kafka import Consumer, KafkaError
from django.conf import settings
from .utils import get_notification_service

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Kafka consumer for handling notification events"""
    
    def __init__(self):
        self.consumer_config = {
            'bootstrap.servers': getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'group.id': getattr(settings, 'KAFKA_CONSUMER_GROUP', 'notification_service'),
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
        }
        self.consumer = Consumer(self.consumer_config)
        self.notification_service = get_notification_service()
        self.running = False
    
    def start_consuming(self, topics=None):
        """Start consuming messages from Kafka topics"""
        if topics is None:
            topics = [
                'user_signed_up',
                'user_verified',
                'user_logged_in',
                'password_reset_requested',
                'hearing_scheduled',
                'case_updated',
                'document_shared',
                'payment_completed'
            ]
        
        self.consumer.subscribe(topics)
        self.running = True
        
        logger.info(f"Starting Kafka consumer for topics: {topics}")
        
        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.info(f"End of partition reached {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                try:
                    # Process the message
                    self.process_message(msg)
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.consumer.close()
            logger.info("Kafka consumer closed")
    
    def stop_consuming(self):
        """Stop the consumer"""
        self.running = False
    
    def process_message(self, msg):
        """Process incoming Kafka message"""
        try:
            topic = msg.topic()
            value = msg.value().decode('utf-8')
            
            logger.info(f"Received message from topic '{topic}': {value}")
            
            # Parse message data - try JSON first
            try:
                message_data = json.loads(value)
                logger.info(f"Successfully parsed JSON message: {message_data}")
            except json.JSONDecodeError:
                # Try comma-separated format as fallback
                if ',' in value and not value.startswith('{'):
                    # Simple comma-separated format: "user_id,email,additional_data"
                    parts = value.split(',')
                    message_data = {
                        'user_id': parts[0] if len(parts) > 0 else '',
                        'email': parts[1] if len(parts) > 1 else '',
                        'additional_data': parts[2:] if len(parts) > 2 else []
                    }
                    logger.info(f"Parsed comma-separated message: {message_data}")
                else:
                    # Fallback: treat as simple string
                    message_data = {'raw_data': value}
                    logger.info(f"Treating as raw data: {message_data}")
            
            # Route message to appropriate handler
            handler_method = f"handle_{topic}"
            if hasattr(self, handler_method):
                getattr(self, handler_method)(message_data)
            else:
                logger.warning(f"No handler found for topic: {topic}")
                
        except Exception as e:
            logger.error(f"Error processing message from topic {msg.topic()}: {str(e)}")
    
    def handle_user_signed_up(self, data: Dict):
        """Handle user signup events"""
        try:
            logger.info(f"Handling user signup event: {data}")
            user_id = data.get('user_id', '')
            email = data.get('email', '').strip()  # Strip whitespace
            username = data.get('username', email.split('@')[0] if email and '@' in email else 'User')
            user_type = data.get('user_type', 'User')
            
            # Validate required fields
            if not user_id:
                logger.error(f"Missing user_id in signup data: {data}")
                return
            
            if not email:
                logger.error(f"Missing email in signup data: {data}")
                return
            
            # Basic email validation
            if '@' not in email or '.' not in email:
                logger.error(f"Invalid email format: {email}")
                return
            
            logger.info(f"Processing user signup for {email} (ID: {user_id})")
            
            # Send welcome notification
            result = self.notification_service.send_welcome_notification(
                user_id=user_id,
                email=email,
                username=username,
                user_type=user_type
            )
            
            if result['success']:
                logger.info(f"Welcome notification sent successfully to {email}")
            else:
                logger.error(f"Failed to send welcome notification to {data}: {result['message']}")
            
            # Send verification notification (for manual testing - prints verification URL)
            import uuid
            verification_token = str(uuid.uuid4())  # Generate a test verification token
            verification_result = self.notification_service.send_verification_notification(
                user_id=user_id,
                email=email,
                username=username,
                verification_token=verification_token,
                user_type=user_type
            )
            
            if verification_result['success']:
                logger.info(f"Verification notification processed for {email}")
            else:
                logger.error(f"Failed to process verification notification for {email}: {verification_result['message']}")
                
        except Exception as e:
            logger.error(f"Error handling user signup: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
    
    def handle_user_verified(self, data: Dict):
        """Handle user email verification events"""
        try:
            user_id = data.get('user_id', '')
            email = data.get('email', '')
            
            if not user_id or not email:
                logger.error(f"Missing required data for user verification: {data}")
                return
            
            logger.info(f"User {email} has been verified")
            
            # You could send a "verification successful" notification here
            # or update user preferences, etc.
            
        except Exception as e:
            logger.error(f"Error handling user verification: {str(e)}")
    
    def handle_user_logged_in(self, data: Dict):
        """Handle user login events"""
        try:
            user_id = data.get('user_id', '')
            email = data.get('email', '')
            
            logger.info(f"User {email} logged in")
            
            # Could send login notifications if enabled
            # or track login events
            
        except Exception as e:
            logger.error(f"Error handling user login: {str(e)}")
    
    def handle_password_reset_requested(self, data: Dict):
        """Handle password reset requests"""
        try:
            user_id = data.get('user_id', '')
            email = data.get('email', '')
            reset_token = data.get('reset_token', '')
            
            if not user_id or not email or not reset_token:
                logger.error(f"Missing required data for password reset: {data}")
                return
            
            logger.info(f"Password reset requested for {email}")
            
            # Send password reset email
            # You would implement this similar to welcome notification
            
        except Exception as e:
            logger.error(f"Error handling password reset: {str(e)}")
    
    def handle_hearing_scheduled(self, data: Dict):
        """Handle hearing scheduling events"""
        try:
            user_id = data.get('user_id', '')
            email = data.get('email', '')
            hearing_date = data.get('hearing_date', '')
            case_number = data.get('case_number', '')
            
            logger.info(f"Hearing scheduled for {email} - Case: {case_number}")
            
            # Send hearing notification
            # Implementation would be similar to welcome notification
            
        except Exception as e:
            logger.error(f"Error handling hearing schedule: {str(e)}")


def start_kafka_consumer():
    """Start Kafka consumer in a separate thread"""
    consumer = KafkaConsumer()
    consumer_thread = threading.Thread(target=consumer.start_consuming)
    consumer_thread.daemon = True
    consumer_thread.start()
    return consumer


# Django management command integration
class KafkaConsumerCommand:
    """Django management command for running Kafka consumer"""
    
    def __init__(self):
        self.consumer = KafkaConsumer()
    
    def handle(self, *args, **options):
        """Handle the management command"""
        topics = options.get('topics', None)
        if topics:
            topics = topics.split(',')
        
        logger.info("Starting Kafka consumer via management command")
        self.consumer.start_consuming(topics)
