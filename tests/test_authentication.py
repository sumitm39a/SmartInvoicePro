"""
Manual test for user authentication.
"""

from src.auth.user_service import authenticate_user


def main() -> None:
    username = input("Enter username: ")
    password = input("Enter password: ")

    user = authenticate_user(username, password)

    if user is None:
        print("\nAuthentication failed!")
        return

    print("\nAuthentication successful!")
    print(f"User ID: {user.user_id}")
    print(f"Username: {user.username}")
    print(f"Role: {user.role}")


if __name__ == "__main__":
    main()