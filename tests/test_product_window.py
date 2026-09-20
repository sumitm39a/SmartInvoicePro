import tkinter as tk

from src.ui.product_window import create_product_window


def main() -> None:
    root = tk.Tk()
    root.withdraw()

    create_product_window(root)

    root.mainloop()


if __name__ == "__main__":
    main()