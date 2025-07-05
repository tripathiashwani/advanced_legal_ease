
# accounts/kafka_producer.py

from confluent_kafka import Producer
from django.conf import settings

producer = Producer({
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
})

def produce_event(topic, value):
    producer.produce(topic, value.encode("utf-8"))
    producer.flush()
