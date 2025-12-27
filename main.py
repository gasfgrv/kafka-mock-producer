from logging import Logger

from flask import Flask, Blueprint

from src.api.producer_controller import create_producer_blueprint
from src.config.logger import configure_logger
from src.config.settings import SCHEMA_PATH, KAFKA_BROKER, SCHEMA_REGISTRY, APP_PORT
from src.kafka.admin import KafkaAdminService
from src.kafka.producer import KafkaProducerService
from src.kafka.schema_registry import AvroSchemaLoader
from src.services.producer_service import ProducerService
from src.validators.avro_validator import AvroValidator


def create_app() -> Flask:
    logger: Logger = configure_logger("mock-producer")

    schema: dict = AvroSchemaLoader(SCHEMA_PATH).load()
    validator: AvroValidator = AvroValidator(schema, logger)
    admin: KafkaAdminService = KafkaAdminService(KAFKA_BROKER, logger)
    producer: KafkaProducerService = KafkaProducerService(KAFKA_BROKER, SCHEMA_REGISTRY, schema, )

    service: ProducerService = ProducerService(admin, validator, producer, logger, )

    app: Flask = Flask(__name__)

    producer_bp: Blueprint = create_producer_blueprint(service, logger)
    app.register_blueprint(producer_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=APP_PORT)
