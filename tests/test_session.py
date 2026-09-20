"""
Manual test for session management.
"""

from src.auth.session import Session
from src.auth.user_service import authenticate_user


def main() -> None:
    username = input("Enter username: ")
    password = input("Enter password: ")

    user = authenticate_user(username, password)

    if user is None:
        print("\nAuthentication failed.")
        return

    session = Session()

    session.login(user)

    print("\nLogin successful!")
    print(f"Logged in user: {session.get_current_user().username}")
    print(f"Role: {session.get_current_user().role}")
    print(f"Is logged in: {session.is_logged_in()}")

    session.logout()

    print("\nAfter logout:")
    print(f"Is logged in: {session.is_logged_in()}")
    print(f"Current user: {session.get_current_user()}")


if __name__ == "__main__":
    main()