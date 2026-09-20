from src.models.user import User


class Session:
    """Store information about the currently logged-in user."""

    def __init__(self):
        self.user: User | None = None

    def login(self, user: User) -> None:
        """Start a session for the given user."""
        self.user = user

    def logout(self) -> None:
        """End the current session."""
        self.user = None

    def is_logged_in(self) -> bool:
        """Return True if a user is currently logged in."""
        return self.user is not None

    def get_current_user(self) -> User | None:
        """Return the currently logged-in user."""
        return self.user