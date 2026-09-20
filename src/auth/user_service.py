from src.auth.password import verify_password
from src.auth.user_repository import find_user_by_username


def authenticate_user(username: str, password: str):
    """
    Authenticate a user using username and password.

    Returns:
        User object if authentication succeeds.
        None if authentication fails.
    """

    username = username.strip()

    if not username or not password:
        return None

    result = find_user_by_username(username)

    if result is None:
        return None

    user, password_hash = result

    if not verify_password(password, password_hash):
        return None

    return user