import tkinter as tk

from src.auth.session import Session
from src.ui.login_window import LoginWindow


def main() -> None:
    session = Session()

    root = tk.Tk()
    LoginWindow(root, session)
    root.mainloop()


if __name__ == "__main__":
    main()