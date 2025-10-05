from django.core.management.base import BaseCommand
from accounts.kafka_producer import kafka_producer
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test Kafka connectivity and message sending'

    def handle(self, *args, **options):
        self.stdout.write('Testing Kafka connectivity...')
        
        # Test data
        test_data = {
            'user_id': 'test-123',
            'email': 'test@example.com',
            'username': 'testuser',
            'user_type': 'PETITIONER',
            'created_at': '2025-10-04T10:00:00Z'
        }
        
        self.stdout.write(f'Kafka producer enabled: {kafka_producer.enabled}')
        self.stdout.write(f'Kafka producer instance: {kafka_producer.producer is not None}')
        
        # Try to send test message
        result = kafka_producer.send_message('user_signed_up', json.dumps(test_data))
        
        if result:
            self.stdout.write(self.style.SUCCESS('✅ Test message sent successfully'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send test message'))
            
        self.stdout.write('Check the logs above for detailed information.')