"""
Temporary test for creating a user.
"""

from getpass import getpass

from src.auth.password import hash_password
from src.database.connection import create_connection


def main() -> None:
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ")
    role = input("Enter role (admin/cashier): ").strip().lower()

    if not username:
        print("Username cannot be empty.")
        return

    if not password:
        print("Password cannot be empty.")
        return

    if role not in ("admin", "cashier"):
        print("Role must be admin or cashier.")
        return

    password_hash = hash_password(password)

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO users (username, password_hash, role, is_active)
            VALUES (%s, %s, %s, TRUE)
        """

        cursor.execute(query, (username, password_hash, role))
        connection.commit()

        print("\nUser created successfully!")
        print(f"Username: {username}")
        print(f"Role: {role}")

    except Exception as error:
        if connection is not None:
            connection.rollback()

        print(f"Could not create user: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()