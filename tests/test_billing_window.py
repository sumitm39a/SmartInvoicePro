import tkinter as tk

from src.ui.billing_window import create_billing_window


def main() -> None:
    root = tk.Tk()
    root.withdraw()

    create_billing_window(root)

    root.mainloop()


if __name__ == "__main__":
    main()