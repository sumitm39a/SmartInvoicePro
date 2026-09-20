"""
Manual test for user repository.
"""

from src.auth.user_repository import find_user_by_username


def main() -> None:
    username = input("Enter username to search: ")

    result = find_user_by_username(username)

    if result is None:
        print("User not found.")
        return

    user, password_hash = result

    print("\nUser found!")
    print(f"User ID: {user.user_id}")
    print(f"Username: {user.username}")
    print(f"Role: {user.role}")
    print(f"Active: {user.is_active}")
    print(f"Password hash exists: {bool(password_hash)}")


if __name__ == "__main__":
    main()