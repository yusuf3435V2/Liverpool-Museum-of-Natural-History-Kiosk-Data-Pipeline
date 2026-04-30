# pylint: disable=logging-fstring-interpolation
import logging
import json
import sys
from dotenv import dotenv_values
from confluent_kafka import Consumer
from datetime import date, datetime, time
import psycopg2


def setup_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def config_setup() -> dict:
    """Load configuration"""
    config = dotenv_values(
        ".env")

    required_keys = [
        "BOOTSTRAP_SERVERS",
        "KAFKA_TOPIC",
        "KAFKA_GROUP_ID",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
    ]

    missing_keys = [key for key in required_keys if not config.get(key)]

    if missing_keys:
        raise ValueError(
            f"Missing required environment variables: {missing_keys}")

    return config


def get_consumer(config) -> Consumer:
    """Returns a kafka consumer"""
    consumer = Consumer({
        "bootstrap.servers": config["BOOTSTRAP_SERVERS"],
        'security.protocol': config["SECURITY_PROTOCOL"],
        'sasl.mechanisms': config["SASL_MECHANISM"],
        'sasl.username': config["USERNAME"],
        'sasl.password': config["PASSWORD"],

        'group.id': config["KAFKA_GROUP_ID"],
        'session.timeout.ms': 6000,
        'auto.offset.reset': 'latest'
    })
    consumer.subscribe([config["KAFKA_TOPIC"]])
    return consumer


def get_database_connection(config):
    """Create and return a PostgreSQL database connection."""
    connection = psycopg2.connect(
        dbname=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"]
    )

    logging.info("Database connection established successfully.")
    return connection


def insert_message(connection, transformed_message):
    """Insert one transformed kiosk interaction into the database."""
    query = """
        INSERT INTO kiosk_interaction (
            exhibition_id,
            rating_value,
            type,
            at
        )
        VALUES (%s, %s, %s, %s);
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    transformed_message["exhibition_id"],
                    transformed_message["rating_value"],
                    transformed_message["type"],
                    transformed_message["at"]
                )
            )

        connection.commit()
        logging.info("Message inserted into database")

    except Exception as error:
        connection.rollback()
        logging.error(f"Failed to insert message into database: {error}")


def receive_messages(consumer, connection):
    """Receive Kafka messages and log a small number of messages for testing."""
    messages_read = 0

    logging.info(
        f"Starting Kafka polling")

    while True:
        message = consumer.poll(1)

        if message is None:
            logging.info("No message received within timeout.")
            continue

        if message.error():
            logging.error(f"Kafka error: {message.error()}")
            continue

        raw_message = message.value().decode("utf-8")
        message_dict = dict_message(raw_message)

        if message_dict is None:
            continue

        if validate_message(message_dict) is False:
            continue

        logging.info(
            f"Received Rating {messages_read + 1}: {message_dict}")
        transformed_message = transform_message(message_dict)
        logging.info(f"Transformed message: {transformed_message}")

        insert_message(connection, transformed_message)

        messages_read += 1


def dict_message(raw_message: str) -> dict:
    """Convert raw message to dict"""
    try:
        return json.loads(raw_message)

    except ValueError:
        logging.warning(
            f"Skipping message because it is not valid JSON: {raw_message}")
        return None


def validate_message(message_dict: dict) -> bool:
    """Validate the message content"""
    required_keys = {"at", "site", "val"}

    valid_rating_values = {-1, 0, 1, 2, 3, 4}
    valid_alert_types = {0, 1}
    valid_site = {0, 1, 2, 3, 4, 5}

    message_keys = set(message_dict.keys())

    if not required_keys.issubset(message_keys):
        logging.warning(f"Skipping message with missing keys: {message_dict}")
        return False

    allowed_keys = {"at", "site", "val", "type"}
    invalid_keys = message_keys - allowed_keys

    if invalid_keys:
        logging.warning(
            f"Skipping message with invalid keys {invalid_keys}: {message_dict}")
        return False

    try:
        interaction_time = datetime.fromisoformat(message_dict["at"])
    except Exception:
        logging.warning(
            f"Skipping message with invalid timestamp: {message_dict}")
        return False

    if interaction_time.time() < time(8, 45) or interaction_time.time() > time(18, 15):
        logging.warning(
            f"Skipping message outside museum operating window: {message_dict}")
        return False

    try:
        rating_value = int(message_dict["val"])
    except Exception:
        logging.warning(
            f"Skipping message with non-integer val: {message_dict}")
        return False

    try:
        site_value = int(message_dict["site"])
    except Exception:
        logging.warning(
            f"Skipping message with non-integer site: {message_dict}")
        return False

    if site_value not in valid_site:
        logging.warning(f"Skipping message with invalid site: {message_dict}")
        return False

    if rating_value not in valid_rating_values:
        logging.warning(f"Skipping message with invalid val: {message_dict}")
        return False

    if "type" in message_dict and message_dict["type"] is not None:
        try:
            alert_type = int(message_dict["type"])
        except Exception:
            logging.warning(
                f"Skipping message with non-integer type: {message_dict}")
            return False

        if alert_type not in valid_alert_types:
            logging.warning(
                f"Skipping message with invalid type: {message_dict}")
            return False

    if rating_value == -1:
        if "type" not in message_dict or message_dict["type"] is None:
            logging.warning(
                f"Skipping alert message missing type: {message_dict}")
            return False

    return True


def transform_message(message):
    """Transform a message into the database schema format."""
    try:
        if 'type' in message and message["type"] is not None:
            assigned_type = int(message["type"])
        else:
            assigned_type = None

        transformed = {
            "exhibition_id": int(message["site"]),
            "rating_value": int(message["val"]),
            "type": assigned_type,
            "at": datetime.fromisoformat(message["at"]).strftime("%Y-%m-%d %H:%M:%S")
        }
        return transformed
    except Exception as error:
        logging.error(f"Error transforming message {message}: {error}")
        return None


def main():
    """Main for Kafka ETL pipeline."""
    setup_logging()
    config = config_setup()
    consumer = get_consumer(config)
    connection = get_database_connection(config)

    try:
        logging.info("Kafka pipeline starting.")
        logging.info(f"Kafka topic: {config['KAFKA_TOPIC']}")
        logging.info(f"Kafka group: {config['KAFKA_GROUP_ID']}")

        logging.info(
            f"Kafka consumer created successfully subscribed to {config['KAFKA_TOPIC']}.")

        receive_messages(consumer, connection)

    except Exception as error:
        logging.error(f"Pipeline failed during setup: {error}")
        sys.exit(1)

    finally:
        consumer.close()
        logging.info("Kafka consumer closed.")

        connection.close()
        logging.info("Database connection closed.")


if __name__ == "__main__":
    main()
