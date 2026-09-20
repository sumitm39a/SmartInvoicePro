import tkinter as tk
from tkinter import ttk, messagebox

from src.auth.session import Session


class Dashboard:
    def __init__(self, root: tk.Tk, session: Session):
        self.root = root
        self.session = session

        # ---------------------------------------------------------
        # Main application window
        # ---------------------------------------------------------

        self.root.title("SmartInvoice Pro - Dashboard")

        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1200x750")

        self.root.minsize(1000, 650)

        # Remove anything left from LoginWindow.
        self.clear_root()

        self.show_dashboard()

    # =============================================================
    # ROOT MANAGEMENT
    # =============================================================

    def clear_root(self):
        """Remove everything from the main application window."""

        for widget in self.root.winfo_children():
            widget.destroy()

    # =============================================================
    # DASHBOARD
    # =============================================================

    def show_dashboard(self):
        """Display the main Dashboard screen."""

        self.clear_root()

        self.root.title("SmartInvoice Pro - Dashboard")

        # ---------------------------------------------------------
        # Main container
        # ---------------------------------------------------------

        main_frame = ttk.Frame(
            self.root,
            padding=40,
        )

        main_frame.pack(
            fill="both",
            expand=True,
        )

        # ---------------------------------------------------------
        # Center container
        # ---------------------------------------------------------

        dashboard_frame = ttk.Frame(
            main_frame,
        )

        dashboard_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------

        title_label = ttk.Label(
            dashboard_frame,
            text="SmartInvoice Pro",
            font=("Arial", 30, "bold"),
        )

        title_label.pack(
            pady=(0, 10),
        )

        # ---------------------------------------------------------
        # Current user
        # ---------------------------------------------------------

        user = self.session.get_current_user()

        if user is not None:

            welcome_label = ttk.Label(
                dashboard_frame,
                text=f"Welcome, {user.username}!",
                font=("Arial", 16),
            )

            welcome_label.pack(
                pady=(0, 5),
            )

            role_label = ttk.Label(
                dashboard_frame,
                text=f"Role: {user.role}",
                font=("Arial", 11),
            )

            role_label.pack(
                pady=(0, 25),
            )

        # ---------------------------------------------------------
        # Description
        # ---------------------------------------------------------

        description_label = ttk.Label(
            dashboard_frame,
            text="Select a module to continue",
            font=("Arial", 12),
        )

        description_label.pack(
            pady=(0, 20),
        )

        # =========================================================
        # MODULE BUTTONS
        # =========================================================

        button_frame = ttk.Frame(
            dashboard_frame,
        )

        button_frame.pack()

        # ---------------------------------------------------------
        # Products
        # ---------------------------------------------------------

        products_button = tk.Button(
            button_frame,
            text="Products",
            width=25,
            height=2,
            font=("Arial", 11),
            command=self.open_products,
        )

        products_button.grid(
            row=0,
            column=0,
            padx=8,
            pady=8,
        )

        # ---------------------------------------------------------
        # Customers
        # ---------------------------------------------------------

        customers_button = tk.Button(
            button_frame,
            text="Customers",
            width=25,
            height=2,
            font=("Arial", 11),
            command=self.open_customers,
        )

        customers_button.grid(
            row=0,
            column=1,
            padx=8,
            pady=8,
        )

        # ---------------------------------------------------------
        # Billing
        # ---------------------------------------------------------

        billing_button = tk.Button(
            button_frame,
            text="Billing",
            width=25,
            height=2,
            font=("Arial", 11),
            command=self.open_billing,
        )

        billing_button.grid(
            row=1,
            column=0,
            padx=8,
            pady=8,
        )

        # ---------------------------------------------------------
        # Invoices
        # ---------------------------------------------------------

        invoices_button = tk.Button(
            button_frame,
            text="Invoices",
            width=25,
            height=2,
            font=("Arial", 11),
            command=self.open_invoices,
        )

        invoices_button.grid(
            row=1,
            column=1,
            padx=8,
            pady=8,
        )

        # ---------------------------------------------------------
        # Payments
        # ---------------------------------------------------------

        payments_button = tk.Button(
            button_frame,
            text="Payments",
            width=25,
            height=2,
            font=("Arial", 11),
            command=self.open_payments,
        )

        payments_button.grid(
            row=2,
            column=0,
            padx=8,
            pady=8,
        )

        # ---------------------------------------------------------
        # Reports
        # ---------------------------------------------------------

        reports_button = tk.Button(
            button_frame,
            text="Reports",
            width=25,
            height=2,
            font=("Arial", 11),
            command=self.open_reports,
        )

        reports_button.grid(
            row=2,
            column=1,
            padx=8,
            pady=8,
        )

        # ---------------------------------------------------------
        # Logout
        # ---------------------------------------------------------

        logout_button = tk.Button(
            dashboard_frame,
            text="Logout",
            width=25,
            height=2,
            font=("Arial", 11),
            command=self.logout,
        )

        logout_button.pack(
            pady=(25, 0),
        )

    # =============================================================
    # MODULE SCREEN HELPER
    # =============================================================

    def create_module_screen(self, title):
        """Replace the dashboard with a module screen and keep navigation visible."""

        self.clear_root()
        self.root.title(f"SmartInvoice Pro - {title}")

        main_frame = ttk.Frame(
            self.root,
            padding=25,
        )

        main_frame.pack(
            fill="both",
            expand=True,
        )

        # =========================================================
        # NAVIGATION AREA
        # =========================================================

        bottom_frame = ttk.Frame(
            main_frame,
        )

        # IMPORTANT:
        # Pack navigation BEFORE the expanding module frame.
        # This guarantees the Back button always gets its own space.
        bottom_frame.pack(
            side="bottom",
            fill="x",
            pady=(15, 0),
        )

        back_button = tk.Button(
            bottom_frame,
            text="← Back to Dashboard",
            width=22,
            height=2,
            font=("Arial", 10, "bold"),
            command=self.show_dashboard,
        )

        back_button.pack(
            side="left",
        )

        # =========================================================
        # MODULE CONTENT
        # =========================================================

        module_frame = ttk.Frame(
            main_frame,
        )

        module_frame.pack(
            fill="both",
            expand=True,
        )

        return module_frame
    # =============================================================
    # PRODUCTS
    # =============================================================

    def open_products(self):
        module_frame = self.create_module_screen("Products")

        from src.ui.product_window import ProductWindow

        ProductWindow(module_frame)
    # =============================================================
    # CUSTOMERS
    # =============================================================

    def open_customers(self):
        """Display Customer Management in the main window."""

        module_frame = self.create_module_screen(
            "Customers"
        )

        from src.ui.customer_window import CustomerWindow

        CustomerWindow(
            module_frame
        )

    # =============================================================
    # BILLING
    # =============================================================

    def open_billing(self):
        """Display Billing in the main application window."""

        self.clear_root()
        self.root.title("SmartInvoice Pro - Billing")

        from src.ui.billing_window import BillingWindow

        BillingWindow(
            self.root,
            self.session,
            self.show_dashboard,
        )

    # =============================================================
    # INVOICES
    # =============================================================

    def open_invoices(self):
        """Display Invoices in the main application window."""

        self.clear_root()
        self.root.title("SmartInvoice Pro - Invoices")

        from src.ui.invoice_window import InvoiceWindow

        InvoiceWindow(
            self.root,
            self.show_dashboard,
        )

    # =============================================================
    # PAYMENTS
    # =============================================================

    def open_payments(self):
        module_frame = self.create_module_screen("Payments")

        from src.ui.payment_window import PaymentWindow

        PaymentWindow(module_frame)
    # =============================================================
    # REPORTS
    # =============================================================

    def open_reports(self):
        module_frame = self.create_module_screen("Reports")

        from src.ui.report_window import ReportWindow

        ReportWindow(
            module_frame,
            back_callback=self.show_dashboard,
        )

    # =============================================================
    # TEMPORARY MESSAGE
    # =============================================================

    def show_module_message(
        self,
        title,
        message,
    ):
        """Temporary message until that module is integrated."""

        messagebox.showinfo(
            title,
            message,
            parent=self.root,
        )

    # =============================================================
    # LOGOUT
    # =============================================================

    def logout(self):

        result = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?",
            parent=self.root,
        )

        if not result:
            return

        self.session.logout()

        self.root.destroy()


# =============================================================
# DASHBOARD FACTORY
# =============================================================

def create_dashboard(session):

    root = tk.Tk()

    Dashboard(
        root,
        session,
    )

    root.mainloop()