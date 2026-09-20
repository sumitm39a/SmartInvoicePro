import tkinter as tk
from tkinter import ttk, messagebox

from src.database.product_repository import (
    add_product,
    get_categories,
    get_all_products,
    update_product,
    delete_product,
)


class ProductWindow:
    """Product management screen for SmartInvoice Pro."""

    def __init__(self, root):
        self.root = root
        self.selected_product_id = None

        self.create_widgets()
        self.load_products()

    def create_widgets(self) -> None:
        """Create the product management interface."""

        # =========================================================
        # HEADER
        # =========================================================

        header_frame = tk.Frame(self.root)
        header_frame.pack(
            fill="x",
            pady=(10, 15),
        )

        title_label = tk.Label(
            header_frame,
            text="Product Management",
            font=("Arial", 22, "bold"),
        )
        title_label.pack(anchor="w")

        # =========================================================
        # FORM
        # =========================================================

        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        # Product Name
        tk.Label(
            form_frame,
            text="Product Name:",
            font=("Arial", 10),
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=8,
            sticky="e",
        )

        self.name_entry = tk.Entry(
            form_frame,
            width=30,
        )
        self.name_entry.grid(
            row=0,
            column=1,
            padx=10,
            pady=8,
        )

        # Category
        tk.Label(
            form_frame,
            text="Category:",
            font=("Arial", 10),
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=8,
            sticky="e",
        )

        self.category_combo = ttk.Combobox(
            form_frame,
            width=27,
            state="readonly",
        )
        self.category_combo.grid(
            row=1,
            column=1,
            padx=10,
            pady=8,
        )

        self.load_categories()

        # Price
        tk.Label(
            form_frame,
            text="Price:",
            font=("Arial", 10),
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=8,
            sticky="e",
        )

        self.price_entry = tk.Entry(
            form_frame,
            width=20,
        )
        self.price_entry.grid(
            row=0,
            column=3,
            padx=10,
            pady=8,
        )

        # Stock
        tk.Label(
            form_frame,
            text="Stock:",
            font=("Arial", 10),
        ).grid(
            row=1,
            column=2,
            padx=10,
            pady=8,
            sticky="e",
        )

        self.stock_entry = tk.Entry(
            form_frame,
            width=20,
        )
        self.stock_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=8,
        )

        # =========================================================
        # BUTTONS
        # =========================================================

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Add Product",
            width=15,
            command=self.add_product,
        ).grid(
            row=0,
            column=0,
            padx=5,
        )

        tk.Button(
            button_frame,
            text="Update",
            width=15,
            command=self.update_selected_product,
        ).grid(
            row=0,
            column=1,
            padx=5,
        )

        tk.Button(
            button_frame,
            text="Delete",
            width=15,
            command=self.delete_selected_product,
        ).grid(
            row=0,
            column=2,
            padx=5,
        )

        tk.Button(
            button_frame,
            text="Clear",
            width=15,
            command=self.clear_fields,
        ).grid(
            row=0,
            column=3,
            padx=5,
        )

        # =========================================================
        # PRODUCT TABLE
        # =========================================================

        table_frame = tk.Frame(self.root)
        table_frame.pack(
            pady=15,
            padx=20,
            fill="both",
            expand=True,
        )

        columns = (
            "ID",
            "Name",
            "Category",
            "Price",
            "Stock",
            "Status",
        )

        self.product_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
        )

        for column in columns:
            self.product_table.heading(
                column,
                text=column,
            )

        self.product_table.column(
            "ID",
            width=50,
            anchor="center",
        )

        self.product_table.column(
            "Name",
            width=180,
        )

        self.product_table.column(
            "Category",
            width=120,
        )

        self.product_table.column(
            "Price",
            width=100,
        )

        self.product_table.column(
            "Stock",
            width=100,
        )

        self.product_table.column(
            "Status",
            width=100,
        )

        self.product_table.pack(
            side="left",
            fill="both",
            expand=True,
        )

        # Select product from table
        self.product_table.bind(
            "<<TreeviewSelect>>",
            self.on_product_select,
        )

        # =========================================================
        # SCROLLBAR
        # =========================================================

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.product_table.yview,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        self.product_table.configure(
            yscrollcommand=scrollbar.set,
        )

    # =========================================================
    # CATEGORIES
    # =========================================================

    def load_categories(self) -> None:
        """Load categories from the database."""

        categories = get_categories()

        self.category_map = {}

        category_names = []

        for category in categories:
            category_id = category["category_id"]
            category_name = category["category_name"]

            self.category_map[category_name] = category_id
            category_names.append(category_name)

        self.category_combo["values"] = category_names

    # =========================================================
    # PRODUCTS
    # =========================================================

    def load_products(self) -> None:
        """Load products from the database."""

        products = get_all_products()

        for item in self.product_table.get_children():
            self.product_table.delete(item)

        for product in products:

            stock = product["stock_quantity"]

            if stock > 0:
                status = "Available"
            else:
                status = "Out of Stock"

            self.product_table.insert(
                "",
                tk.END,
                values=(
                    product["product_id"],
                    product["product_name"],
                    product["category_name"],
                    product["price"],
                    stock,
                    status,
                ),
            )

    # =========================================================
    # SELECT PRODUCT
    # =========================================================

    def on_product_select(self, event=None) -> None:
        """Load the selected product into the form."""

        selected = self.product_table.selection()

        if not selected:
            return

        item = self.product_table.item(selected[0])

        values = item.get("values")

        if not values:
            return

        self.selected_product_id = int(values[0])

        product_name = values[1]
        category_name = values[2]
        price = values[3]
        stock = values[4]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, product_name)

        self.category_combo.set(category_name)

        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, price)

        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, stock)

    # =========================================================
    # VALIDATE
    # =========================================================

    def validate_fields(self):
        """Validate product form data."""

        name = self.name_entry.get().strip()
        category_name = self.category_combo.get().strip()
        price_text = self.price_entry.get().strip()
        stock_text = self.stock_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Missing Information",
                "Product name is required.",
                parent=self.root.winfo_toplevel(),
            )
            return None

        if not category_name:
            messagebox.showwarning(
                "Missing Information",
                "Please select a category.",
                parent=self.root.winfo_toplevel(),
            )
            return None

        if not price_text or not stock_text:
            messagebox.showwarning(
                "Missing Information",
                "Price and stock are required.",
                parent=self.root.winfo_toplevel(),
            )
            return None

        if len(name) < 2:
            messagebox.showwarning(
                "Invalid Product Name",
                "Product name must contain at least 2 characters.",
                parent=self.root.winfo_toplevel(),
            )
            return None

        category_id = self.category_map.get(category_name)

        if category_id is None:
            messagebox.showerror(
                "Invalid Category",
                "Please select a valid category.",
                parent=self.root.winfo_toplevel(),
            )
            return None

        try:
            price = float(price_text)
            stock = int(stock_text)

            if price <= 0:
                raise ValueError

            if stock < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Price must be greater than 0 and stock must be a whole number of 0 or more.",
                parent=self.root.winfo_toplevel(),
            )
            return None

        return {
            "name": name,
            "category_id": category_id,
            "price": price,
            "stock": stock,
        }

    # =========================================================
    # ADD PRODUCT
    # =========================================================

    def add_product(self) -> None:
        """Add a new product."""

        data = self.validate_fields()

        if data is None:
            return

        try:
            add_product(
                category_id=data["category_id"],
                name=data["name"],
                description=None,
                price=data["price"],
                stock_quantity=data["stock"],
            )

            messagebox.showinfo(
                "Success",
                "Product added successfully!",
                parent=self.root.winfo_toplevel(),
            )

            self.clear_fields()
            self.load_products()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not add product.\n\n{error}",
                parent=self.root.winfo_toplevel(),
            )

    # =========================================================
    # UPDATE PRODUCT
    # =========================================================

    def update_selected_product(self) -> None:
        """Update the selected product."""

        if self.selected_product_id is None:
            messagebox.showwarning(
                "No Product Selected",
                "Please select a product from the table first.",
                parent=self.root.winfo_toplevel(),
            )
            return

        data = self.validate_fields()

        if data is None:
            return

        try:
            update_product(
                product_id=self.selected_product_id,
                category_id=data["category_id"],
                name=data["name"],
                price=data["price"],
                stock_quantity=data["stock"],
            )

            messagebox.showinfo(
                "Success",
                "Product updated successfully!",
                parent=self.root.winfo_toplevel(),
            )

            self.clear_fields()
            self.load_products()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not update product.\n\n{error}",
                parent=self.root.winfo_toplevel(),
            )

    # =========================================================
    # DELETE PRODUCT
    # =========================================================

    def delete_selected_product(self) -> None:
        """Delete the selected product."""

        if self.selected_product_id is None:
            messagebox.showwarning(
                "No Product Selected",
                "Please select a product from the table first.",
                parent=self.root.winfo_toplevel(),
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected product?",
            parent=self.root.winfo_toplevel(),
        )

        if not confirm:
            return

        try:
            delete_product(self.selected_product_id)

            messagebox.showinfo(
                "Success",
                "Product deleted successfully!",
                parent=self.root.winfo_toplevel(),
            )

            self.clear_fields()
            self.load_products()

        except Exception as error:
            messagebox.showerror(
                "Cannot Delete Product",
                str(error),
                parent=self.root.winfo_toplevel(),
            )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear_fields(self) -> None:
        """Clear product input fields."""

        self.selected_product_id = None

        self.name_entry.delete(
            0,
            tk.END,
        )

        self.category_combo.set("")

        self.price_entry.delete(
            0,
            tk.END,
        )

        self.stock_entry.delete(
            0,
            tk.END,
        )

        self.product_table.selection_remove(
            self.product_table.selection()
        )

        self.name_entry.focus()


# =============================================================
# BACKWARD-COMPATIBLE FACTORY
# =============================================================

def create_product_window(parent: tk.Tk) -> None:
    """
    Open Product Management.

    Retained for compatibility with older code.
    """

    product_root = tk.Toplevel(parent)

    ProductWindow(
        product_root,
    )