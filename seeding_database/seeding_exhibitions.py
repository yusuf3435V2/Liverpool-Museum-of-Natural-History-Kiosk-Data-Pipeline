import os
import json
from datetime import datetime
import psycopg2
from dotenv import dotenv_values


JSON_FOLDER = "./exhibition_data/json"
config = dotenv_values(".env")
connection = psycopg2.connect(
    dbname=config["DB_NAME"],
    user=config["DB_USER"],
    host=config["DB_HOST"],
    port=config["DB_PORT"]
)


def format_exhibition_id(raw_id):
    """Convert IDs like 'EXH_00' into integers like 0."""
    return int(raw_id.replace("EXH_", ""))


def format_start_date(raw_date):
    """Convert dates like '23/08/21' into Python date objects."""
    return datetime.strptime(raw_date, "%d/%m/%y").date()


def load_json_file(file_path):
    """Open and return the contents of one JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def insert_exhibition(cursor, exhibition_data):
    """Transform one exhibition record and insert it into the exhibition table."""
    exhibition_id = format_exhibition_id(exhibition_data["EXHIBITION_ID"])
    exhibition_name = exhibition_data["EXHIBITION_NAME"]
    floor = exhibition_data["FLOOR"]
    department = exhibition_data["DEPARTMENT"]
    start_date = format_start_date(exhibition_data["START_DATE"])
    description = exhibition_data["DESCRIPTION"]

    query = """
        INSERT INTO exhibition (
            exhibition_id,
            exhibition_name,
            floor,
            department,
            start_date,
            description
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (exhibition_id) DO NOTHING;
    """

    cursor.execute(
        query,
        (
            exhibition_id,
            exhibition_name,
            floor,
            department,
            start_date,
            description
        )
    )

    print(f"Inserted exhibition {exhibition_id}: {exhibition_name}")


if __name__ == "__main__":
    try:
        with connection.cursor() as cursor:
            for file_name in os.listdir(JSON_FOLDER):
                file_path = os.path.join(JSON_FOLDER, file_name)
                exhibition_data = load_json_file(file_path)
                insert_exhibition(cursor, exhibition_data)
            connection.commit()
        print("All exhibition data loaded successfully.")

    except Exception as error:
        print(f"Error loading exhibition data: {error}")

    connection.close()
