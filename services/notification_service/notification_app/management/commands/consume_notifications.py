from django.core.management.base import BaseCommand
from notification_app.kafka_consumer import KafkaConsumer


class Command(BaseCommand):
    help = 'Start Kafka consumer for notification service'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topics',
            type=str,
            help='Comma-separated list of topics to consume from',
        )

    def handle(self, *args, **options):
        consumer = KafkaConsumer()
        
        topics = options.get('topics')
        if topics:
            topics = topics.split(',')
            self.stdout.write(
                self.style.SUCCESS(f'Starting Kafka consumer for topics: {topics}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Starting Kafka consumer for all notification topics')
            )
        
        try:
            consumer.start_consuming(topics)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Kafka consumer stopped by user')
            )
