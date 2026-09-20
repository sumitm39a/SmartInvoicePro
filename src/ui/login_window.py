import tkinter as tk
from tkinter import messagebox

from src.auth.session import Session
from src.auth.user_service import authenticate_user


class LoginWindow:
    """Login screen for SmartInvoice Pro."""

    def __init__(self, root: tk.Tk, session: Session):
        self.root = root
        self.session = session

        # ---------------------------------------------------------
        # Main application window
        # ---------------------------------------------------------

        self.root.title("SmartInvoice Pro - Login")

        # Start maximized.
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1200x700")

        self.root.minsize(1000, 650)

        self.create_widgets()

    def create_widgets(self) -> None:
        """Create the login interface."""

        # Remove anything already inside the main window.
        for widget in self.root.winfo_children():
            widget.destroy()

        # ---------------------------------------------------------
        # Main login container
        # ---------------------------------------------------------

        main_frame = tk.Frame(self.root)
        main_frame.pack(
            fill="both",
            expand=True,
        )

        # Center container.
        login_frame = tk.Frame(main_frame)

        login_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------

        title_label = tk.Label(
            login_frame,
            text="SmartInvoice Pro",
            font=("Arial", 30, "bold"),
        )
        title_label.pack(
            pady=(0, 10),
        )

        # ---------------------------------------------------------
        # Subtitle
        # ---------------------------------------------------------

        subtitle_label = tk.Label(
            login_frame,
            text="Login to continue",
            font=("Arial", 14),
        )
        subtitle_label.pack(
            pady=(0, 30),
        )

        # ---------------------------------------------------------
        # Username
        # ---------------------------------------------------------

        username_label = tk.Label(
            login_frame,
            text="Username",
            font=("Arial", 12),
        )
        username_label.pack()

        self.username_entry = tk.Entry(
            login_frame,
            width=35,
            font=("Arial", 12),
        )
        self.username_entry.pack(
            pady=(6, 18),
            ipady=4,
        )

        # ---------------------------------------------------------
        # Password
        # ---------------------------------------------------------

        password_label = tk.Label(
            login_frame,
            text="Password",
            font=("Arial", 12),
        )
        password_label.pack()

        self.password_entry = tk.Entry(
            login_frame,
            width=35,
            font=("Arial", 12),
            show="*",
        )
        self.password_entry.pack(
            pady=(6, 25),
            ipady=4,
        )

        # ---------------------------------------------------------
        # Login button
        # ---------------------------------------------------------

        login_button = tk.Button(
            login_frame,
            text="LOGIN",
            width=25,
            height=2,
            font=("Arial", 11, "bold"),
            command=self.handle_login,
        )
        login_button.pack()

        # Pressing Enter also performs login.
        self.password_entry.bind(
            "<Return>",
            lambda event: self.handle_login(),
        )

        self.username_entry.focus()

    def handle_login(self) -> None:
        """Authenticate the entered username and password."""

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Login Required",
                "Please enter username and password.",
                parent=self.root,
            )
            return

        user = authenticate_user(
            username,
            password,
        )

        if user is None:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password.",
                parent=self.root,
            )

            self.password_entry.delete(
                0,
                tk.END,
            )

            self.password_entry.focus()
            return

        # Store the authenticated user.
        self.session.login(user)

        messagebox.showinfo(
            "Login Successful",
            f"Welcome, {user.username}!",
            parent=self.root,
        )

        # IMPORTANT:
        # Do NOT destroy the root.
        #
        # We keep the same Tk window and replace
        # the login screen with the dashboard.
        from src.ui.dashboard import Dashboard

        Dashboard(
            root=self.root,
            session=self.session,
        )


def create_login_window(session: Session) -> None:
    """
    Backward-compatible login factory.

    This function is kept so existing imports do not immediately
    break, but the main application now creates the Tk root itself.
    """

    root = tk.Tk()

    LoginWindow(
        root=root,
        session=session,
    )

    root.mainloop()