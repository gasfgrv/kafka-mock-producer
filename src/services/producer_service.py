from logging import Logger

from src.kafka.admin import KafkaAdminService
from src.kafka.producer import KafkaProducerService
from src.validators.avro_validator import AvroValidator


class ProducerService:
    logger: Logger
    producer: KafkaProducerService
    validator: AvroValidator
    admin: KafkaAdminService

    def __init__(self, admin: KafkaAdminService, validator: AvroValidator, producer: KafkaProducerService,
                 logger: Logger):
        self.admin = admin
        self.validator = validator
        self.producer = producer
        self.logger = logger

    def produce(self, topic: str, message: dict):
        if not self.admin.topic_exists(topic):
            self.logger.error(f"Topic {topic} does not exist")
            raise ValueError(f"Topic {topic} does not exist")

        if not self.validator.is_valid(message):
            self.logger.error(f"Message {message} is not valid")
            raise ValueError(f"Message {message} is not valid")

        self.logger.info(f"Sending message {message}")
        self.producer.send(topic, message)
