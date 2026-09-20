import tkinter as tk
from tkinter import ttk, messagebox

from src.reports.report_repository import (
    get_sales_summary,
    get_product_sales_report,
    get_payment_summary,
    get_date_wise_sales_report,
)


class ReportWindow:
    def __init__(self, root, back_callback=None):
        self.root = root
        self.back_callback = back_callback

        self.setup_style()
        self.create_widgets()
        self.load_reports()

    # ---------------------------------------------------------
    # STYLE
    # ---------------------------------------------------------

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
            "Section.TLabel",
            font=("Segoe UI", 13, "bold"),
        )

        style.configure(
            "Summary.TLabel",
            font=("Segoe UI", 11),
        )

        style.configure(
            "SummaryValue.TLabel",
            font=("Segoe UI", 16, "bold"),
        )

        style.configure(
            "Treeview",
            rowheight=30,
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

    # ---------------------------------------------------------
    # MAIN UI
    # ---------------------------------------------------------

    def create_widgets(self):

        main_frame = ttk.Frame(
            self.root,
            padding=20,
        )

        main_frame.pack(
            fill="both",
            expand=True,
        )

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header_frame = ttk.Frame(main_frame)

        header_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        title_label = ttk.Label(
            header_frame,
            text="Sales & Payment Reports",
            style="Title.TLabel",
        )

        title_label.pack(
            side="left",
        )

        refresh_button = ttk.Button(
            header_frame,
            text="Refresh Reports",
            command=self.load_reports,
            style="Primary.TButton",
        )

        refresh_button.pack(
            side="right",
        )

        # -----------------------------------------------------
        # SUMMARY CARDS
        # -----------------------------------------------------

        self.summary_frame = ttk.Frame(main_frame)

        self.summary_frame.pack(
            fill="x",
            pady=(0, 20),
        )

        self.create_summary_cards()

        # -----------------------------------------------------
        # NOTEBOOK / REPORT TABS
        # -----------------------------------------------------

        self.notebook = ttk.Notebook(main_frame)

        self.notebook.pack(
            fill="both",
            expand=True,
        )

        self.product_tab = ttk.Frame(
            self.notebook,
            padding=10,
        )

        self.payment_tab = ttk.Frame(
            self.notebook,
            padding=10,
        )

        self.date_tab = ttk.Frame(
            self.notebook,
            padding=10,
        )

        self.notebook.add(
            self.product_tab,
            text="Product Sales",
        )

        self.notebook.add(
            self.payment_tab,
            text="Payment Summary",
        )

        self.notebook.add(
            self.date_tab,
            text="Date-wise Sales",
        )

        self.create_product_report()
        self.create_payment_report()
        self.create_date_report()

    # ---------------------------------------------------------
    # SUMMARY CARDS
    # ---------------------------------------------------------

    def create_summary_cards(self):

        self.summary_values = {}

        cards = [
            ("Total Invoices", "total_invoices"),
            ("Total Sales", "total_sales"),
            ("Paid Invoices", "paid_invoices"),
            ("Pending Invoices", "pending_invoices"),
            ("Failed Invoices", "failed_invoices"),
        ]

        for index, (title, key) in enumerate(cards):

            card = ttk.LabelFrame(
                self.summary_frame,
                text=title,
                padding=12,
            )

            card.grid(
                row=0,
                column=index,
                padx=5,
                sticky="nsew",
            )

            self.summary_frame.columnconfigure(
                index,
                weight=1,
            )

            value_label = ttk.Label(
                card,
                text="0",
                style="SummaryValue.TLabel",
                anchor="center",
            )

            value_label.pack(
                fill="x",
                pady=5,
            )

            self.summary_values[key] = value_label

    # ---------------------------------------------------------
    # PRODUCT SALES REPORT
    # ---------------------------------------------------------

    def create_product_report(self):

        section_label = ttk.Label(
            self.product_tab,
            text="Product Sales Report",
            style="Section.TLabel",
        )

        section_label.pack(
            anchor="w",
            pady=(0, 10),
        )

        table_frame = ttk.Frame(
            self.product_tab,
        )

        table_frame.pack(
            fill="both",
            expand=True,
        )

        columns = (
            "product_id",
            "product_name",
            "quantity_sold",
            "sales_amount",
        )

        self.product_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
        )

        self.product_tree.heading(
            "product_id",
            text="Product ID",
        )

        self.product_tree.heading(
            "product_name",
            text="Product Name",
        )

        self.product_tree.heading(
            "quantity_sold",
            text="Quantity Sold",
        )

        self.product_tree.heading(
            "sales_amount",
            text="Sales Amount",
        )

        self.product_tree.column(
            "product_id",
            width=100,
            anchor="center",
        )

        self.product_tree.column(
            "product_name",
            width=300,
            anchor="w",
        )

        self.product_tree.column(
            "quantity_sold",
            width=150,
            anchor="center",
        )

        self.product_tree.column(
            "sales_amount",
            width=180,
            anchor="e",
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.product_tree.yview,
        )

        self.product_tree.configure(
            yscrollcommand=scrollbar.set,
        )

        self.product_tree.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

    # ---------------------------------------------------------
    # PAYMENT REPORT
    # ---------------------------------------------------------

    def create_payment_report(self):

        section_label = ttk.Label(
            self.payment_tab,
            text="Payment Summary",
            style="Section.TLabel",
        )

        section_label.pack(
            anchor="w",
            pady=(0, 10),
        )

        table_frame = ttk.Frame(
            self.payment_tab,
        )

        table_frame.pack(
            fill="both",
            expand=True,
        )

        columns = (
            "payment_method",
            "payment_count",
            "total_amount",
            "successful_payments",
            "failed_payments",
        )

        self.payment_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
        )

        self.payment_tree.heading(
            "payment_method",
            text="Payment Method",
        )

        self.payment_tree.heading(
            "payment_count",
            text="Payment Count",
        )

        self.payment_tree.heading(
            "total_amount",
            text="Total Amount",
        )

        self.payment_tree.heading(
            "successful_payments",
            text="Successful",
        )

        self.payment_tree.heading(
            "failed_payments",
            text="Failed",
        )

        self.payment_tree.column(
            "payment_method",
            width=180,
            anchor="center",
        )

        self.payment_tree.column(
            "payment_count",
            width=150,
            anchor="center",
        )

        self.payment_tree.column(
            "total_amount",
            width=180,
            anchor="e",
        )

        self.payment_tree.column(
            "successful_payments",
            width=150,
            anchor="center",
        )

        self.payment_tree.column(
            "failed_payments",
            width=150,
            anchor="center",
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.payment_tree.yview,
        )

        self.payment_tree.configure(
            yscrollcommand=scrollbar.set,
        )

        self.payment_tree.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

    # ---------------------------------------------------------
    # DATE-WISE SALES REPORT
    # ---------------------------------------------------------

    def create_date_report(self):

        section_label = ttk.Label(
            self.date_tab,
            text="Date-wise Sales Report",
            style="Section.TLabel",
        )

        section_label.pack(
            anchor="w",
            pady=(0, 10),
        )

        table_frame = ttk.Frame(
            self.date_tab,
        )

        table_frame.pack(
            fill="both",
            expand=True,
        )

        columns = (
            "sale_date",
            "invoice_count",
            "total_sales",
        )

        self.date_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
        )

        self.date_tree.heading(
            "sale_date",
            text="Sale Date",
        )

        self.date_tree.heading(
            "invoice_count",
            text="Invoice Count",
        )

        self.date_tree.heading(
            "total_sales",
            text="Total Sales",
        )

        self.date_tree.column(
            "sale_date",
            width=250,
            anchor="center",
        )

        self.date_tree.column(
            "invoice_count",
            width=200,
            anchor="center",
        )

        self.date_tree.column(
            "total_sales",
            width=220,
            anchor="e",
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.date_tree.yview,
        )

        self.date_tree.configure(
            yscrollcommand=scrollbar.set,
        )

        self.date_tree.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

    # ---------------------------------------------------------
    # LOAD ALL REPORTS
    # ---------------------------------------------------------

    def load_reports(self):

        try:
            self.load_sales_summary()
            self.load_product_sales()
            self.load_payment_summary()
            self.load_date_wise_sales()

        except Exception as error:

            messagebox.showerror(
                "Report Error",
                f"Could not load reports.\n\n{error}",
                parent=self.root.winfo_toplevel(),
            )

    # ---------------------------------------------------------
    # LOAD SALES SUMMARY
    # ---------------------------------------------------------

    def load_sales_summary(self):

        summary = get_sales_summary()

        total_invoices = (
            summary.get("total_invoices") or 0
        )

        total_sales = (
            summary.get("total_sales") or 0
        )

        paid_invoices = (
            summary.get("paid_invoices") or 0
        )

        pending_invoices = (
            summary.get("pending_invoices") or 0
        )

        failed_invoices = (
            summary.get("failed_invoices") or 0
        )

        self.summary_values[
            "total_invoices"
        ].config(
            text=str(total_invoices)
        )

        self.summary_values[
            "total_sales"
        ].config(
            text=f"₹{float(total_sales):,.2f}"
        )

        self.summary_values[
            "paid_invoices"
        ].config(
            text=str(paid_invoices)
        )

        self.summary_values[
            "pending_invoices"
        ].config(
            text=str(pending_invoices)
        )

        self.summary_values[
            "failed_invoices"
        ].config(
            text=str(failed_invoices)
        )

    # ---------------------------------------------------------
    # LOAD PRODUCT SALES
    # ---------------------------------------------------------

    def load_product_sales(self):

        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        products = get_product_sales_report()

        for product in products:

            product_id = product.get(
                "product_id"
            )

            product_name = product.get(
                "product_name",
                "",
            )

            quantity_sold = product.get(
                "quantity_sold"
            ) or 0

            sales_amount = product.get(
                "sales_amount"
            ) or 0

            self.product_tree.insert(
                "",
                "end",
                values=(
                    product_id,
                    product_name,
                    quantity_sold,
                    f"₹{float(sales_amount):,.2f}",
                ),
            )

    # ---------------------------------------------------------
    # LOAD PAYMENT SUMMARY
    # ---------------------------------------------------------

    def load_payment_summary(self):

        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)

        payments = get_payment_summary()

        for payment in payments:

            payment_method = payment.get(
                "payment_method",
                "",
            )

            payment_count = payment.get(
                "payment_count"
            ) or 0

            total_amount = payment.get(
                "total_amount"
            ) or 0

            successful_payments = payment.get(
                "successful_payments"
            ) or 0

            failed_payments = payment.get(
                "failed_payments"
            ) or 0

            self.payment_tree.insert(
                "",
                "end",
                values=(
                    payment_method,
                    payment_count,
                    f"₹{float(total_amount):,.2f}",
                    successful_payments,
                    failed_payments,
                ),
            )

    # ---------------------------------------------------------
    # LOAD DATE-WISE SALES
    # ---------------------------------------------------------

    def load_date_wise_sales(self):

        for item in self.date_tree.get_children():
            self.date_tree.delete(item)

        sales = get_date_wise_sales_report()

        for row in sales:

            sale_date = row.get(
                "sale_date"
            )

            invoice_count = row.get(
                "invoice_count"
            ) or 0

            total_sales = row.get(
                "total_sales"
            ) or 0

            if sale_date is not None:

                if hasattr(sale_date, "strftime"):
                    sale_date = sale_date.strftime(
                        "%Y-%m-%d"
                    )
                else:
                    sale_date = str(sale_date)

            else:
                sale_date = ""

            self.date_tree.insert(
                "",
                "end",
                values=(
                    sale_date,
                    invoice_count,
                    f"₹{float(total_sales):,.2f}",
                ),
            )


# -------------------------------------------------------------
# FACTORY
# -------------------------------------------------------------

def create_report_window(
    parent,
    back_callback=None,
) -> None:

    ReportWindow(
        parent,
        back_callback,
    )