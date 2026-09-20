

import mysql.connector
from mysql.connector import Error, MySQLConnection

from src.config.settings import get_database_config


def create_connection() -> MySQLConnection:
    """
    Create and return a new MySQL connection.

    Caller is responsible for closing the connection when finished.
    """
    config = get_database_config()

    try:
        connection = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
        )
        return connection

    except Error as error:
        raise ConnectionError(
            f"Could not connect to MySQL database '{config['database']}': {error}"
        ) from error
