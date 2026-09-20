from src.database.connection import create_connection
from src.models.user import User


def find_user_by_username(username: str):
    """
    Find an active user by username.

    Returns:
        tuple[User, str] | None
        User object and password hash if found.
        None if the user does not exist.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                user_id,
                username,
                password_hash,
                role,
                is_active
            FROM users
            WHERE username = %s
              AND is_active = TRUE
            LIMIT 1
        """

        cursor.execute(query, (username,))

        row = cursor.fetchone()

        if row is None:
            return None

        user = User(
            user_id=row["user_id"],
            username=row["username"],
            role=row["role"],
            is_active=bool(row["is_active"]),
        )

        password_hash = row["password_hash"]

        return user, password_hash

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()