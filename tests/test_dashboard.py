from src.auth.session import Session
from src.auth.user_service import authenticate_user
from src.ui.dashboard import create_dashboard


def main() -> None:
    username = input("Enter username: ")
    password = input("Enter password: ")

    user = authenticate_user(username, password)

    if user is None:
        print("Authentication failed.")
        return

    session = Session()
    session.login(user)

    create_dashboard(session)


if __name__ == "__main__":
    main()