from src.auth.session import Session
from src.ui.login_window import create_login_window


def main() -> None:
    session = Session()
    create_login_window(session)


if __name__ == "__main__":
    main()