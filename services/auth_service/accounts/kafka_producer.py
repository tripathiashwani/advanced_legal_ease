
# accounts/kafka_producer.py

from kafka import KafkaProducer
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class SafeKafkaProducer:
    def __init__(self):
        self.producer = None
        # self.enabled = getattr(settings, 'KAFKA_ENABLED', False)
        self.enabled=False
        
        logger.info(f"Initializing Kafka producer. Enabled: {self.enabled}")
        logger.info(f"Kafka bootstrap servers: {getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'NOT SET')}")
        
        if self.enabled:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    api_version=(0, 10, 1),
                    request_timeout_ms=10000,
                    retries=3
                )
                logger.info("Kafka producer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Kafka producer: {e}")
                logger.warning(f"Exception type: {type(e).__name__}")
                import traceback
                logger.warning(f"Full traceback: {traceback.format_exc()}")
                self.enabled = False
        else:
            logger.info("Kafka producer disabled by configuration")
    
    def send_message(self, topic, message):
        logger.debug(f"send_message called with topic: {topic}, enabled: {self.enabled}, producer: {self.producer is not None}")
        
        if not self.enabled or not self.producer:
            logger.info(f"Kafka disabled. Would send to {topic}: {message}")
            return False
        
        try:
            logger.debug(f"Attempting to send message to topic {topic}")
            
            # Convert message to dict if it's a string
            if isinstance(message, str):
                message_data = json.loads(message)
            else:
                message_data = message
                
            logger.debug(f"Sending message data: {message_data}")
            future = self.producer.send(topic, message_data)
            logger.debug(f"Message sent, flushing...")
            self.producer.flush(timeout=10)
            logger.info(f"Successfully sent message to {topic}: {message_data}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def close(self):
        if self.producer:
            self.producer.close()

# Global instance
kafka_producer = SafeKafkaProducer()

def produce_event(topic, message):
    """Legacy function for backward compatibility"""
    return kafka_producer.send_message(topic, message)
