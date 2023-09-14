import psycopg2
import os


class DatabaseConnection:
    """
    Context manager for postgres database connection
    """
    def __init__(self, database_url):
        self.database_url = database_url

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(self.database_url)
            return self.conn
        except psycopg2.Error as e:
            raise Exception(f"Error connecting to the database: {e}")

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
        if exc_type is not None:
            print(f"An exception of type {exc_type} occurred: {exc_value}")
            return False


def write_to_db(url: str, filename: str, uuid: str, task: str, status: str) -> None:
    """
    Writes request metadata to the tracking table
    :param url:
    :param filename:
    :param uuid:
    :param task:
    :param status:
    :return:
    """
    create_table(url)
    extension = os.path.splitext(filename)[1].lstrip(".")

    with DatabaseConnection(url) as conn:
        cursor = conn.cursor()
        insert_query = "INSERT INTO your_table (id, file_name, file_extension, task, status) VALUES (%s, %s, %s, %s, %s)"
        data_to_insert = (uuid, filename, extension, task, status)
        cursor.execute(insert_query, data_to_insert)
        conn.commit()
    return


def create_table(url: str) -> None:
    """
    Makes sure the database table to track the service request exists, and if not creates the table with the required
    schema
    :param url:
    :return:
    """
    with DatabaseConnection(url) as conn:
        cursor = conn.cursor()
        cursor.execute(
        """CREATE TABLE IF NOT EXISTS service_tracker (
        id SERIAL PRIMARY KEY,
        file_name VARCHAR(255),
        file_extension VARCHAR(255)
        task VARCHAR(255)
        status VARCHAR(255)
        )"""
        )
        conn.commit()
    return


