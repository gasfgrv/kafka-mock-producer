from logging import Logger

from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, ClusterMetadata


class KafkaAdminService:
    logger: Logger
    client: AdminClient

    def __init__(self, broker: str, logger: Logger):
        self.client = AdminClient({"bootstrap.servers": broker})
        self.logger = logger

    def topic_exists(self, topic: str) -> bool:
        try:
            self.logger.info(f"Checking if topic {topic} exists")
            metadata: ClusterMetadata = self.client.list_topics(timeout=5)
            return topic in metadata.topics
        except KafkaException as e:
            self.logger.error(f"Erro verificando tópico: {e}")
            return False
