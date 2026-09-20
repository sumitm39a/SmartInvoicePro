import tkinter as tk
from tkinter import ttk, messagebox

from src.database.payment_repository import get_all_payments


class PaymentWindow:
    """
    Payment Management screen for SmartInvoice Pro.

    This screen is designed to run inside the main Dashboard window.
    It does not create a separate Toplevel window.
    """

    def __init__(self, root):
        self.root = root

        self.payments = []

        self.setup_style()
        self.create_widgets()
        self.load_payments()

    # =========================================================
    # STYLE
    # =========================================================

    def setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold"),
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10),
        )

        style.configure(
            "Treeview",
            rowheight=32,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
        )

    # =========================================================
    # CREATE UI
    # =========================================================

    def create_widgets(self):

        # -----------------------------------------------------
        # Main container
        # -----------------------------------------------------

        main_frame = ttk.Frame(
            self.root,
            padding=20,
        )

        main_frame.pack(
            fill="both",
            expand=True,
        )

        # -----------------------------------------------------
        # Header
        # -----------------------------------------------------

        header_frame = ttk.Frame(main_frame)

        header_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        ttk.Label(
            header_frame,
            text="Payments",
            style="Title.TLabel",
        ).pack(
            anchor="w",
        )

        ttk.Label(
            header_frame,
            text="View payment transactions and their status.",
            style="Subtitle.TLabel",
        ).pack(
            anchor="w",
            pady=(3, 0),
        )

        # -----------------------------------------------------
        # Button bar
        # -----------------------------------------------------

        button_frame = ttk.Frame(main_frame)

        button_frame.pack(
            fill="x",
            pady=(0, 10),
        )

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_payments,
            style="Primary.TButton",
        ).pack(
            side="left",
        )

        # -----------------------------------------------------
        # Payment table
        # -----------------------------------------------------

        table_frame = ttk.Frame(main_frame)

        table_frame.pack(
            fill="both",
            expand=True,
        )

        columns = (
            "payment_id",
            "invoice_number",
            "payment_method",
            "transaction_id",
            "amount",
            "payment_status",
            "payment_time",
        )

        self.payment_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        # -----------------------------------------------------
        # Headings
        # -----------------------------------------------------

        self.payment_tree.heading(
            "payment_id",
            text="Payment ID",
        )

        self.payment_tree.heading(
            "invoice_number",
            text="Invoice",
        )

        self.payment_tree.heading(
            "payment_method",
            text="Method",
        )

        self.payment_tree.heading(
            "transaction_id",
            text="Transaction ID",
        )

        self.payment_tree.heading(
            "amount",
            text="Amount",
        )

        self.payment_tree.heading(
            "payment_status",
            text="Status",
        )

        self.payment_tree.heading(
            "payment_time",
            text="Payment Time",
        )

        # -----------------------------------------------------
        # Columns
        # -----------------------------------------------------

        self.payment_tree.column(
            "payment_id",
            width=90,
            anchor="center",
        )

        self.payment_tree.column(
            "invoice_number",
            width=180,
            anchor="center",
        )

        self.payment_tree.column(
            "payment_method",
            width=120,
            anchor="center",
        )

        self.payment_tree.column(
            "transaction_id",
            width=220,
            anchor="w",
        )

        self.payment_tree.column(
            "amount",
            width=130,
            anchor="e",
        )

        self.payment_tree.column(
            "payment_status",
            width=120,
            anchor="center",
        )

        self.payment_tree.column(
            "payment_time",
            width=170,
            anchor="center",
        )

        # -----------------------------------------------------
        # Scrollbars
        # -----------------------------------------------------

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.payment_tree.yview,
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.payment_tree.xview,
        )

        self.payment_tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.payment_tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        table_frame.rowconfigure(
            0,
            weight=1,
        )

        table_frame.columnconfigure(
            0,
            weight=1,
        )

        # -----------------------------------------------------
        # Status label
        # -----------------------------------------------------

        self.status_label = ttk.Label(
            main_frame,
            text="",
            style="Subtitle.TLabel",
        )

        self.status_label.pack(
            anchor="w",
            pady=(10, 0),
        )

    # =========================================================
    # LOAD PAYMENTS
    # =========================================================

    def load_payments(self):
        """
        Load all payment records from MySQL.
        """

        try:
            self.payments = get_all_payments()

            # Clear existing rows.
            for item in self.payment_tree.get_children():
                self.payment_tree.delete(item)

            # Add payment records.
            for payment in self.payments:

                payment_time = payment.get("payment_time")

                if payment_time is not None:
                    payment_time = payment_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    payment_time = "-"

                transaction_id = (
                    payment.get("transaction_id")
                    or "-"
                )

                amount = payment.get("amount")

                if amount is not None:
                    amount_text = f"₹{float(amount):,.2f}"
                else:
                    amount_text = "₹0.00"

                invoice_number = (
                    payment.get("invoice_number")
                    or "-"
                )

                payment_method = (
                    payment.get("payment_method")
                    or "-"
                )

                payment_status = (
                    payment.get("payment_status")
                    or "-"
                )

                self.payment_tree.insert(
                    "",
                    "end",
                    iid=str(payment["payment_id"]),
                    values=(
                        payment["payment_id"],
                        invoice_number,
                        payment_method,
                        transaction_id,
                        amount_text,
                        payment_status,
                        payment_time,
                    ),
                )

            self.status_label.config(
                text=f"{len(self.payments)} payment(s) found."
            )

        except Exception as error:

            messagebox.showerror(
                "Payment Error",
                f"Could not load payments.\n\n{error}",
                parent=self.root.winfo_toplevel(),
            )

    # =========================================================
    # FACTORY FUNCTION
    # =========================================================

    def refresh(self):
        """
        Public refresh method.

        Kept simple so the Dashboard or another module can
        refresh payment data if required later.
        """

        self.load_payments()


# =============================================================
# BACKWARD-COMPATIBLE FACTORY
# =============================================================

def create_payment_window(parent: tk.Tk) -> None:
    """
    Open Payment Management in a separate window.

    This function is retained for compatibility with older code.

    The new Dashboard navigation should directly create:

        PaymentWindow(module_frame)

    instead of using this factory.
    """

    payment_root = tk.Toplevel(parent)

    payment_root.title(
        "SmartInvoice Pro - Payments"
    )

    payment_root.geometry(
        "1150x650"
    )

    payment_root.minsize(
        1000,
        600,
    )

    PaymentWindow(
        payment_root,
    )