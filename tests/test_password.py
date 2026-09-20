"""
Manual test for password hashing and verification.
"""

from src.auth.password import hash_password, verify_password


def main() -> None:
    password = "TestPassword123"

    # Create a bcrypt hash
    password_hash = hash_password(password)

    print("Password hash generated successfully!")
    print(f"Hash: {password_hash}")

    # Test correct password
    if verify_password(password, password_hash):
        print("Correct password: verification successful!")
    else:
        print("Correct password: verification failed!")

    # Test incorrect password
    if not verify_password("WrongPassword", password_hash):
        print("Wrong password: correctly rejected!")
    else:
        print("Wrong password: incorrectly accepted!")


if __name__ == "__main__":
    main()