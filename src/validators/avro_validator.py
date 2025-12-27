from logging import Logger

from fastavro import parse_schema, validate


class AvroValidator:
    logger: Logger
    parsed_schema: str | list | dict

    def __init__(self, schema: dict, logger: Logger):
        self.parsed_schema = parse_schema(schema)
        self.logger = logger

    def is_valid(self, message: dict) -> bool:
        try:
            self.logger.info(f"Validating message against schema")
            return validate(message, self.parsed_schema)
        except Exception as e:
            self.logger.error(f"Failed to validate message: {e}")
            return False
