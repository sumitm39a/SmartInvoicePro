import tkinter as tk

from src.ui.customer_window import create_customer_window


def main() -> None:
    root = tk.Tk()
    root.withdraw()

    create_customer_window(root)

    root.mainloop()


if __name__ == "__main__":
    main()