import os
import tkinter as tk
from tkinter import ttk, messagebox

from src.database.invoice_repository import (
    get_all_invoices,
    get_invoice_items,
)
from src.reports.invoice_pdf import generate_invoice_pdf


class InvoiceWindow:
    def __init__(self, root, back_callback=None):
        self.root = root
        self.back_callback = back_callback

        self.invoices = []

        self.setup_style()
        self.create_widgets()
        self.load_invoices()

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
    # MAIN UI
    # =========================================================

    def create_widgets(self):
        """
        Create the Invoices screen inside the existing main window.
        """

        # ---------------------------------------------------------
        # Main container
        # ---------------------------------------------------------

        main_frame = ttk.Frame(
            self.root,
            padding=25,
        )

        main_frame.pack(
            fill="both",
            expand=True,
        )

        # ---------------------------------------------------------
        # Header
        # ---------------------------------------------------------

        header_frame = ttk.Frame(main_frame)

        header_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        ttk.Label(
            header_frame,
            text="Invoices",
            style="Title.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="View saved invoices and their payment status.",
            style="Subtitle.TLabel",
        ).pack(
            anchor="w",
            pady=(3, 0),
        )

        # ---------------------------------------------------------
        # Button bar
        # ---------------------------------------------------------

        button_frame = ttk.Frame(main_frame)

        button_frame.pack(
            fill="x",
            pady=(0, 10),
        )

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_invoices,
            style="Primary.TButton",
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="View Details",
            command=self.view_selected_invoice,
            style="Primary.TButton",
        ).pack(
            side="left",
            padx=(10, 0),
        )

        ttk.Button(
            button_frame,
            text="Generate PDF",
            command=self.generate_selected_invoice_pdf,
            style="Primary.TButton",
        ).pack(
            side="left",
            padx=(10, 0),
        )

        # ---------------------------------------------------------
        # Invoice table
        # ---------------------------------------------------------

        table_frame = ttk.Frame(main_frame)

        table_frame.pack(
            fill="both",
            expand=True,
        )

        columns = (
            "invoice_number",
            "customer_name",
            "mobile_number",
            "invoice_date",
            "grand_total",
            "payment_status",
        )

        self.invoice_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.invoice_tree.heading(
            "invoice_number",
            text="Invoice Number",
        )

        self.invoice_tree.heading(
            "customer_name",
            text="Customer",
        )

        self.invoice_tree.heading(
            "mobile_number",
            text="Mobile",
        )

        self.invoice_tree.heading(
            "invoice_date",
            text="Date",
        )

        self.invoice_tree.heading(
            "grand_total",
            text="Grand Total",
        )

        self.invoice_tree.heading(
            "payment_status",
            text="Payment Status",
        )

        self.invoice_tree.column(
            "invoice_number",
            width=180,
            anchor="center",
        )

        self.invoice_tree.column(
            "customer_name",
            width=180,
            anchor="w",
        )

        self.invoice_tree.column(
            "mobile_number",
            width=130,
            anchor="center",
        )

        self.invoice_tree.column(
            "invoice_date",
            width=160,
            anchor="center",
        )

        self.invoice_tree.column(
            "grand_total",
            width=130,
            anchor="e",
        )

        self.invoice_tree.column(
            "payment_status",
            width=130,
            anchor="center",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.invoice_tree.yview,
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.invoice_tree.xview,
        )

        self.invoice_tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.invoice_tree.grid(
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

        # Double-click opens invoice details.
        self.invoice_tree.bind(
            "<Double-1>",
            lambda event: self.view_selected_invoice(),
        )

        # ---------------------------------------------------------
        # Status
        # ---------------------------------------------------------

        self.status_label = ttk.Label(
            main_frame,
            text="",
            style="Subtitle.TLabel",
        )

        self.status_label.pack(
            anchor="w",
            pady=(10, 0),
        )

        # ---------------------------------------------------------
        # Bottom navigation
        # ---------------------------------------------------------

        if self.back_callback is not None:

            navigation_frame = ttk.Frame(main_frame)

            navigation_frame.pack(
                fill="x",
                pady=(15, 0),
            )

            tk.Button(
                navigation_frame,
                text="← Back to Dashboard",
                font=("Segoe UI", 10, "bold"),
                bg="#ffffff",
                fg="#2563eb",
                activebackground="#ffffff",
                activeforeground="#1d4ed8",
                relief="solid",
                bd=1,
                cursor="hand2",
                command=self.back_callback,
                padx=18,
                pady=7,
            ).pack(
                side="left",
            )

    # =========================================================
    # LOAD INVOICES
    # =========================================================

    def load_invoices(self):
        try:
            self.invoices = get_all_invoices()

            # Clear existing rows.
            for item in self.invoice_tree.get_children():
                self.invoice_tree.delete(item)

            # Add invoices to table.
            for invoice in self.invoices:

                invoice_date = invoice.get("invoice_date")

                if invoice_date is not None:
                    invoice_date = invoice_date.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                else:
                    invoice_date = ""

                grand_total = invoice.get(
                    "grand_total",
                    0,
                )

                if grand_total is not None:
                    grand_total = f"₹{float(grand_total):,.2f}"
                else:
                    grand_total = "₹0.00"

                customer_name = (
                    invoice.get("customer_name")
                    or "Walk-in Customer"
                )

                mobile_number = (
                    invoice.get("mobile_number")
                    or "-"
                )

                self.invoice_tree.insert(
                    "",
                    "end",
                    iid=str(invoice["invoice_id"]),
                    values=(
                        invoice["invoice_number"],
                        customer_name,
                        mobile_number,
                        invoice_date,
                        grand_total,
                        invoice["payment_status"],
                    ),
                )

            self.status_label.config(
                text=f"{len(self.invoices)} invoice(s) found."
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Could not load invoices.\n\n{error}",
                parent=self.root,
            )

    # =========================================================
    # GET SELECTED INVOICE
    # =========================================================

    def get_selected_invoice(self):

        selected = self.invoice_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Invoice",
                "Please select an invoice first.",
                parent=self.root,
            )
            return None

        invoice_id = int(selected[0])

        for invoice in self.invoices:

            if int(invoice["invoice_id"]) == invoice_id:
                return invoice

        messagebox.showerror(
            "Error",
            "Selected invoice could not be found.",
            parent=self.root,
        )

        return None

    # =========================================================
    # VIEW SELECTED INVOICE
    # =========================================================

    def view_selected_invoice(self):

        invoice = self.get_selected_invoice()

        if invoice is None:
            return

        try:

            items = get_invoice_items(
                invoice_id=int(invoice["invoice_id"])
            )

            self.open_invoice_details(
                invoice,
                items,
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Could not load invoice details.\n\n{error}",
                parent=self.root,
            )

    # =========================================================
    # GENERATE PDF
    # =========================================================

    def generate_selected_invoice_pdf(self):
        """
        Generate and open the PDF for the selected invoice.
        """

        invoice = self.get_selected_invoice()

        if invoice is None:
            return

        invoice_id = int(invoice["invoice_id"])
        invoice_number = invoice["invoice_number"]

        try:

            pdf_path = generate_invoice_pdf(
                invoice_id=invoice_id
            )

            messagebox.showinfo(
                "PDF Generated",
                f"Invoice PDF generated successfully.\n\n"
                f"Invoice: {invoice_number}\n\n"
                f"Saved at:\n{pdf_path}",
                parent=self.root,
            )

            # Open the generated PDF using the default
            # Windows PDF application.
            os.startfile(pdf_path)

        except Exception as error:

            messagebox.showerror(
                "PDF Error",
                f"Could not generate invoice PDF.\n\n{error}",
                parent=self.root,
            )

    # =========================================================
    # INVOICE DETAILS
    # =========================================================

    def open_invoice_details(self, invoice, items):

        details_window = tk.Toplevel(self.root)

        details_window.title(
            f"Invoice - {invoice['invoice_number']}"
        )

        details_window.geometry("850x600")
        details_window.minsize(750, 500)

        main_frame = ttk.Frame(
            details_window,
            padding=20,
        )

        main_frame.pack(
            fill="both",
            expand=True,
        )

        # ---------------------------------------------------------
        # Invoice header
        # ---------------------------------------------------------

        ttk.Label(
            main_frame,
            text="Invoice Details",
            style="Title.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            main_frame,
            text=invoice["invoice_number"],
            font=("Segoe UI", 12, "bold"),
        ).pack(
            anchor="w",
            pady=(5, 15),
        )

        # ---------------------------------------------------------
        # Customer / invoice information
        # ---------------------------------------------------------

        info_frame = ttk.LabelFrame(
            main_frame,
            text="Invoice Information",
            padding=12,
        )

        info_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        invoice_date = invoice.get("invoice_date")

        if invoice_date is not None:
            invoice_date = invoice_date.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            invoice_date = "-"

        customer_name = (
            invoice.get("customer_name")
            or "Walk-in Customer"
        )

        mobile_number = (
            invoice.get("mobile_number")
            or "-"
        )

        ttk.Label(
            info_frame,
            text=f"Customer: {customer_name}",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 40),
            pady=4,
        )

        ttk.Label(
            info_frame,
            text=f"Mobile: {mobile_number}",
        ).grid(
            row=0,
            column=1,
            sticky="w",
            pady=4,
        )

        ttk.Label(
            info_frame,
            text=f"Date: {invoice_date}",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 40),
            pady=4,
        )

        ttk.Label(
            info_frame,
            text=f"Payment Status: {invoice['payment_status']}",
        ).grid(
            row=1,
            column=1,
            sticky="w",
            pady=4,
        )

        # ---------------------------------------------------------
        # Items table
        # ---------------------------------------------------------

        ttk.Label(
            main_frame,
            text="Purchased Items",
            font=("Segoe UI", 11, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 7),
        )

        items_frame = ttk.Frame(main_frame)

        items_frame.pack(
            fill="both",
            expand=True,
        )

        columns = (
            "product_name",
            "quantity",
            "price",
            "subtotal",
        )

        items_tree = ttk.Treeview(
            items_frame,
            columns=columns,
            show="headings",
        )

        items_tree.heading(
            "product_name",
            text="Product",
        )

        items_tree.heading(
            "quantity",
            text="Quantity",
        )

        items_tree.heading(
            "price",
            text="Price",
        )

        items_tree.heading(
            "subtotal",
            text="Subtotal",
        )

        items_tree.column(
            "product_name",
            width=350,
            anchor="w",
        )

        items_tree.column(
            "quantity",
            width=100,
            anchor="center",
        )

        items_tree.column(
            "price",
            width=130,
            anchor="e",
        )

        items_tree.column(
            "subtotal",
            width=150,
            anchor="e",
        )

        scrollbar = ttk.Scrollbar(
            items_frame,
            orient="vertical",
            command=items_tree.yview,
        )

        items_tree.configure(
            yscrollcommand=scrollbar.set,
        )

        items_tree.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        for item in items:

            price = float(
                item["price_at_sale"]
            )

            subtotal = float(
                item["subtotal"]
            )

            items_tree.insert(
                "",
                "end",
                values=(
                    item["product_name"],
                    item["quantity"],
                    f"₹{price:,.2f}",
                    f"₹{subtotal:,.2f}",
                ),
            )

        # ---------------------------------------------------------
        # Total / remarks
        # ---------------------------------------------------------

        bottom_frame = ttk.Frame(main_frame)

        bottom_frame.pack(
            fill="x",
            pady=(12, 0),
        )

        remarks = invoice.get("remarks") or "-"

        ttk.Label(
            bottom_frame,
            text=f"Remarks: {remarks}",
        ).pack(side="left")

        ttk.Label(
            bottom_frame,
            text=(
                f"Grand Total: "
                f"₹{float(invoice['grand_total']):,.2f}"
            ),
            font=("Segoe UI", 12, "bold"),
        ).pack(side="right")

        ttk.Button(
            main_frame,
            text="Close",
            command=details_window.destroy,
            style="Primary.TButton",
        ).pack(
            anchor="e",
            pady=(15, 0),
        )


# =============================================================
# FACTORY
# =============================================================

def create_invoice_window(
    parent,
    back_callback=None,
) -> None:
    """
    Open the invoice screen inside the provided main window.
    """

    InvoiceWindow(
        parent,
        back_callback,
    )