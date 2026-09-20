import re
import tkinter as tk
from tkinter import ttk, messagebox

from src.database.customer_repository import (
    add_customer,
    get_all_customers,
    delete_customer,
)


class CustomerWindow:
    """Customer management screen for SmartInvoice Pro."""

    def __init__(self, root):
        self.root = root
        self.selected_customer_id = None

        self.create_widgets()
        self.load_customers()

    # =========================================================
    # UI
    # =========================================================

    def create_widgets(self) -> None:

        title_label = tk.Label(
            self.root,
            text="Customer Management",
            font=("Arial", 22, "bold"),
        )

        title_label.pack(
            pady=(20, 15),
        )

        form_frame = tk.Frame(self.root)

        form_frame.pack(
            pady=10,
        )

        # Customer Name

        tk.Label(
            form_frame,
            text="Customer Name:",
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

        # Phone

        tk.Label(
            form_frame,
            text="Phone:",
            font=("Arial", 10),
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=8,
            sticky="e",
        )

        self.phone_entry = tk.Entry(
            form_frame,
            width=25,
        )

        self.phone_entry.grid(
            row=0,
            column=3,
            padx=10,
            pady=8,
        )

        # Email

        tk.Label(
            form_frame,
            text="Email:",
            font=("Arial", 10),
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=8,
            sticky="e",
        )

        self.email_entry = tk.Entry(
            form_frame,
            width=30,
        )

        self.email_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=8,
        )

        # Address

        tk.Label(
            form_frame,
            text="Address:",
            font=("Arial", 10),
        ).grid(
            row=1,
            column=2,
            padx=10,
            pady=8,
            sticky="e",
        )

        self.address_entry = tk.Entry(
            form_frame,
            width=25,
        )

        self.address_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=8,
        )

        # =====================================================
        # BUTTONS
        # =====================================================

        button_frame = tk.Frame(self.root)

        button_frame.pack(
            pady=15,
        )

        tk.Button(
            button_frame,
            text="Add Customer",
            width=15,
            command=self.add_customer,
        ).grid(
            row=0,
            column=0,
            padx=5,
        )

        tk.Button(
            button_frame,
            text="Delete",
            width=15,
            command=self.delete_selected_customer,
        ).grid(
            row=0,
            column=1,
            padx=5,
        )

        tk.Button(
            button_frame,
            text="Clear",
            width=15,
            command=self.clear_fields,
        ).grid(
            row=0,
            column=2,
            padx=5,
        )

        # =====================================================
        # CUSTOMER TABLE
        # =====================================================

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
            "Phone",
            "Email",
            "Address",
        )

        self.customer_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
        )

        for column in columns:

            self.customer_table.heading(
                column,
                text=column,
            )

        self.customer_table.column(
            "ID",
            width=50,
            anchor="center",
        )

        self.customer_table.column(
            "Name",
            width=180,
        )

        self.customer_table.column(
            "Phone",
            width=130,
        )

        self.customer_table.column(
            "Email",
            width=180,
        )

        self.customer_table.column(
            "Address",
            width=250,
        )

        self.customer_table.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.customer_table.yview,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        self.customer_table.configure(
            yscrollcommand=scrollbar.set,
        )

        self.customer_table.bind(
            "<<TreeviewSelect>>",
            self.on_customer_selected,
        )

        self.name_entry.focus()

    # =========================================================
    # SELECT CUSTOMER
    # =========================================================

    def on_customer_selected(self, event=None):

        selection = self.customer_table.selection()

        if not selection:
            self.selected_customer_id = None
            return

        values = self.customer_table.item(
            selection[0],
            "values",
        )

        if not values:
            return

        self.selected_customer_id = int(
            values[0]
        )

        self.name_entry.delete(
            0,
            tk.END,
        )

        self.name_entry.insert(
            0,
            values[1],
        )

        self.phone_entry.delete(
            0,
            tk.END,
        )

        self.phone_entry.insert(
            0,
            values[2],
        )

        self.email_entry.delete(
            0,
            tk.END,
        )

        self.email_entry.insert(
            0,
            values[3],
        )

        self.address_entry.delete(
            0,
            tk.END,
        )

        self.address_entry.insert(
            0,
            values[4],
        )

    # =========================================================
    # VALIDATE CUSTOMER
    # =========================================================

    def validate_customer_fields(self):

        name = self.name_entry.get().strip()
        mobile = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            raise ValueError(
                "Customer name is required."
            )

        if len(name) < 2:
            raise ValueError(
                "Customer name must contain at least 2 characters."
            )

        if not mobile:
            raise ValueError(
                "Mobile number is required."
            )

        if not mobile.isdigit():
            raise ValueError(
                "Mobile number should contain only digits."
            )

        if len(mobile) != 10:
            raise ValueError(
                "Mobile number must contain exactly 10 digits."
            )

        if mobile[0] not in "6789":
            raise ValueError(
                "Please enter a valid 10-digit Indian mobile number."
            )

        if email:
            email_pattern = (
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            )

            if not re.match(
                email_pattern,
                email,
            ):
                raise ValueError(
                    "Please enter a valid email address."
                )

        if not address:
            raise ValueError(
                "Customer address is required."
            )

        if len(address) < 3:
            raise ValueError(
                "Please enter a meaningful address."
            )

        return (
            name,
            mobile,
            email or None,
            address,
        )

    # =========================================================
    # ADD CUSTOMER
    # =========================================================

    def add_customer(self) -> None:

        try:

            (
                name,
                mobile,
                email,
                address,
            ) = self.validate_customer_fields()

        except ValueError as error:

            messagebox.showwarning(
                "Invalid Customer",
                str(error),
                parent=self.root.winfo_toplevel(),
            )

            return

        try:

            add_customer(
                name=name,
                mobile_number=mobile,
                email=email,
                address=address,
            )

            messagebox.showinfo(
                "Success",
                "Customer added successfully.",
                parent=self.root.winfo_toplevel(),
            )

            self.clear_fields()
            self.load_customers()

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Could not add customer:\n\n{error}",
                parent=self.root.winfo_toplevel(),
            )

    # =========================================================
    # LOAD CUSTOMERS
    # =========================================================

    def load_customers(self) -> None:

        try:

            customers = get_all_customers()

            for item in self.customer_table.get_children():
                self.customer_table.delete(item)

            for customer in customers:

                self.customer_table.insert(
                    "",
                    tk.END,
                    values=(
                        customer["customer_id"],
                        customer["customer_name"],
                        customer["mobile_number"] or "",
                        customer["email"] or "",
                        customer["address"] or "",
                    ),
                )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Could not load customers:\n{error}",
                parent=self.root.winfo_toplevel(),
            )

    # =========================================================
    # DELETE CUSTOMER
    # =========================================================

    def delete_selected_customer(self) -> None:

        if self.selected_customer_id is None:

            messagebox.showwarning(
                "Select Customer",
                "Please select a customer from the table first.",
                parent=self.root.winfo_toplevel(),
            )

            return

        customer_name = self.name_entry.get().strip()

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{customer_name}'?",
            parent=self.root.winfo_toplevel(),
        )

        if not confirm:
            return

        try:

            delete_customer(
                self.selected_customer_id
            )

            messagebox.showinfo(
                "Success",
                "Customer deleted successfully.",
                parent=self.root.winfo_toplevel(),
            )

            self.clear_fields()
            self.load_customers()

        except Exception as error:

            messagebox.showerror(
                "Cannot Delete Customer",
                str(error),
                parent=self.root.winfo_toplevel(),
            )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear_fields(self) -> None:

        self.selected_customer_id = None

        self.name_entry.delete(
            0,
            tk.END,
        )

        self.phone_entry.delete(
            0,
            tk.END,
        )

        self.email_entry.delete(
            0,
            tk.END,
        )

        self.address_entry.delete(
            0,
            tk.END,
        )

        for item in self.customer_table.selection():
            self.customer_table.selection_remove(item)

        self.name_entry.focus()


# =============================================================
# BACKWARD-COMPATIBLE FACTORY
# =============================================================

def create_customer_window(parent: tk.Tk) -> None:

    customer_root = tk.Toplevel(parent)

    CustomerWindow(
        customer_root,
    )