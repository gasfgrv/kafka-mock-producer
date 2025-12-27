import os

KAFKA_BROKER: str = os.getenv("KAFKA_BROKER", "localhost:9092")
SCHEMA_REGISTRY: str = os.getenv("SCHEMA_REGISTRY", "http://localhost:8081")
SCHEMA_PATH: str = os.getenv("SCHEMA_PATH", "./schemas/user.avsc")
APP_PORT: int = int(os.getenv("APP_PORT", 5000))
