"""
SmartInvoice Pro entry point.

Run from the project root:
    python -m src.main
"""

import tkinter as tk

from src.auth.session import Session
from src.ui.login_window import LoginWindow


def main() -> None:
    """Start SmartInvoice Pro."""

    session = Session()

    # Create ONE main Tkinter application window.
    root = tk.Tk()

    # Start the application with the login screen.
    LoginWindow(
        root=root,
        session=session,
    )

    root.mainloop()


if __name__ == "__main__":
    main()