"""
Manual connection test for Phase 3.

Run from project root:
    python -m tests.test_connection
"""

from src.database.connection import create_connection


def main() -> None:
    connection = None
    cursor = None

    try:
        connection = create_connection()

        if not connection.is_connected():
            print("Connection object returned, but not connected.")
            return

        print("MySQL connection successful!")

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()[0]
        print(f"Connected to database: {database_name}")

        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"Tables found: {len(tables)}")

        for (table_name,) in tables:
            print(f"  - {table_name}")

    except ConnectionError as error:
        print(error)

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            print("Connection closed.")


if __name__ == "__main__":
    main()
