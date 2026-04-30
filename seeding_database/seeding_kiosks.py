import csv
from datetime import datetime
import psycopg2
from dotenv import dotenv_values


CSV_FILE = "./kiosk_data/combined_kiosk_data.csv"
config = dotenv_values(".env")
connection = psycopg2.connect(
    dbname=config["DB_NAME"],
    user=config["DB_USER"],
    password=config["DB_PASSWORD"],
    host=config["DB_HOST"],
    port=config["DB_PORT"],
    sslmode="require"
)


def format_timestamp(raw_timestamp):
    """Convert timestamp string into a Python datetime object."""
    return datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S")


def format_type(raw_type, raw_val):
    """Convert kiosk type values into readable text."""

    if raw_val != "-1":
        return None

    if raw_type == "0":
        return "assistance"
    if raw_type == "1":
        return "emergency"

    return None


def insert_kiosk_row(cursor, row):
    """Transform and insert one kiosk row into the database."""

    exhibition_id = int(row["site"])
    rating_value = int(row["val"])
    interaction_time = format_timestamp(row["at"])
    interaction_type = format_type(row["type"], row["val"])

    query = """
        INSERT INTO kiosk_interaction (
            exhibition_id,
            rating_value,
            type,
            at
        )
        VALUES (%s, %s, %s, %s);
    """

    cursor.execute(
        query,
        (
            exhibition_id,
            rating_value,
            interaction_type,
            interaction_time
        )
    )


if __name__ == "__main__":
    try:
        with connection.cursor() as cursor:
            with open(CSV_FILE, "r", encoding="utf-8") as file:
                csv_rows = csv.DictReader(file)
                for row in csv_rows:
                    insert_kiosk_row(cursor, row)

            connection.commit()
        print("All kiosk data loaded successfully.")

    except Exception as error:
        print(f"Error loading kiosk data: {error}")

    connection.close()
