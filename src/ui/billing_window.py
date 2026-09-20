import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import time
import webbrowser
from urllib.parse import urlencode

from PIL import Image, ImageTk

from src.database.product_repository import get_all_products
from src.database.customer_repository import get_all_customers
from src.database.invoice_repository import save_invoice
from src.auth.session import Session
from src.config.settings import PROJECT_ROOT, get_env
from src.services.upi_qr_service import generate_upi_qr
from src.services.payment_service import create_payment_order
from src.api.payment_callback import start_callback_server


# The Flask callback server is shared by Billing windows.
_callback_server_thread = None
_callback_server_lock = threading.Lock()


def ensure_callback_server_running() -> None:
    """Start the local Razorpay callback server once in the background."""
    global _callback_server_thread

    with _callback_server_lock:
        if (
            _callback_server_thread is not None
            and _callback_server_thread.is_alive()
        ):
            return

        _callback_server_thread = threading.Thread(
            target=start_callback_server,
            daemon=True,
        )
        _callback_server_thread.start()


class BillingWindow:
    """Modern billing interface for SmartInvoice Pro."""

    def __init__(self, root, session: Session, back_callback=None):
        self.root = root
        self.session = session
        self.back_callback = back_callback

        self.products = []
        self.customers = []
        self.cart = []

        # Stores the invoice created from the current cart.
        # These values will also be used by the payment/QR flow later.
        self.current_invoice_id = None
        self.current_invoice_number = None

        self.setup_style()
        self.create_widgets()

        self.load_customers()
        self.load_products()

    def setup_style(self) -> None:
        """Configure ttk styles."""

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Modern.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(15, 9),
        )

        style.configure(
            "Add.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(15, 9),
        )

        style.configure(
            "Modern.TCombobox",
            font=("Segoe UI", 10),
            padding=6,
        )

        style.configure(
            "Modern.Treeview",
            font=("Segoe UI", 10),
            rowheight=32,
        )

        style.configure(
            "Modern.Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            padding=8,
        )

    def create_widgets(self) -> None:
        """Create the billing interface."""

        main_frame = tk.Frame(
            self.root,
            bg="#f4f6f8",
        )
        main_frame.pack(
            fill="both",
            expand=True,
        )

        # =====================================================
        # HEADER
        # =====================================================

        header = tk.Frame(
            main_frame,
            bg="#ffffff",
            height=90,
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        title_frame = tk.Frame(
            header,
            bg="#ffffff",
        )
        title_frame.pack(
            side="left",
            padx=25,
            pady=12,
        )

        tk.Label(
            title_frame,
            text="SmartInvoice Pro",
            font=("Segoe UI", 18, "bold"),
            bg="#ffffff",
            fg="#1f2937",
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Create New Invoice",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(anchor="w")

        tk.Label(
            header,
            text="NEW INVOICE",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#2563eb",
        ).pack(
            side="right",
            padx=30,
        )

        # =====================================================
        # BOTTOM NAVIGATION
        # =====================================================

        if self.back_callback is not None:
            navigation = tk.Frame(
                main_frame,
                bg="#f4f6f8",
                height=55,
            )
            navigation.pack(
                side="bottom",
                fill="x",
                padx=25,
                pady=(0, 12),
            )
            navigation.pack_propagate(False)

            tk.Button(
                navigation,
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
            ).pack(side="left")

        # =====================================================
        # CONTENT
        # =====================================================

        content_area = tk.Frame(
            main_frame,
            bg="#f4f6f8",
        )
        content_area.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(18, 10),
        )

        # Keep the billing workspace centered instead of stretching every
        # section across the full monitor width.
        content = tk.Frame(
            content_area,
            bg="#f4f6f8",
            width=1240,
        )
        content.pack(
            fill="both",
            expand=True,
            padx=0,
            pady=0,
        )

        # =====================================================
        # LEFT SIDE
        # =====================================================

        left_frame = tk.Frame(
            content,
            bg="#f4f6f8",
        )
        left_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12),
        )

        # =====================================================
        # CUSTOMER CARD
        # =====================================================

        customer_card = tk.Frame(
            left_frame,
            bg="#ffffff",
        )
        customer_card.pack(
            fill="x",
            pady=(0, 15),
        )

        tk.Label(
            customer_card,
            text="CUSTOMER",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 8),
        )

        customer_row = tk.Frame(
            customer_card,
            bg="#ffffff",
        )
        customer_row.pack(
            fill="x",
            padx=20,
            pady=(0, 18),
        )

        self.customer_combo = ttk.Combobox(
            customer_row,
            state="readonly",
            style="Modern.TCombobox",
        )
        self.customer_combo.pack(
            side="left",
            fill="x",
            expand=True,
        )

        # =====================================================
        # PRODUCT CARD
        # =====================================================

        product_card = tk.Frame(
            left_frame,
            bg="#ffffff",
        )
        product_card.pack(
            fill="x",
            pady=(0, 15),
        )

        tk.Label(
            product_card,
            text="ADD PRODUCT",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 10),
        )

        product_row = tk.Frame(
            product_card,
            bg="#ffffff",
        )
        product_row.pack(
            fill="x",
            padx=20,
            pady=(0, 10),
        )

        # Product
        product_section = tk.Frame(
            product_row,
            bg="#ffffff",
        )
        product_section.pack(
            side="left",
            fill="x",
            expand=True,
        )

        tk.Label(
            product_section,
            text="Product",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(anchor="w")

        self.product_combo = ttk.Combobox(
            product_section,
            state="readonly",
            style="Modern.TCombobox",
        )
        self.product_combo.pack(
            fill="x",
            pady=(4, 0),
        )

        self.product_combo.bind(
            "<<ComboboxSelected>>",
            self.on_product_selected,
        )

        # Quantity
        quantity_section = tk.Frame(
            product_row,
            bg="#ffffff",
        )
        quantity_section.pack(
            side="left",
            padx=(15, 0),
        )

        tk.Label(
            quantity_section,
            text="Quantity",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(anchor="w")

        self.quantity_entry = tk.Entry(
            quantity_section,
            width=10,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
        )
        self.quantity_entry.pack(
            pady=(4, 0),
            ipady=7,
        )
        self.quantity_entry.insert(0, "1")

        # Price
        price_section = tk.Frame(
            product_row,
            bg="#ffffff",
        )
        price_section.pack(
            side="left",
            padx=(15, 0),
        )

        tk.Label(
            price_section,
            text="Price",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(anchor="w")

        self.price_label = tk.Label(
            price_section,
            text="₹ 0.00",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#1f2937",
        )
        self.price_label.pack(
            pady=(9, 0),
        )

        ttk.Button(
            product_card,
            text="+  Add to Cart",
            style="Add.TButton",
            command=self.add_to_cart,
        ).pack(
            anchor="e",
            padx=20,
            pady=(5, 18),
        )

        # =====================================================
        # CART
        # =====================================================

        cart_card = tk.Frame(
            left_frame,
            bg="#ffffff",
        )
        cart_card.pack(
            fill="both",
            expand=True,
        )

        cart_header = tk.Frame(
            cart_card,
            bg="#ffffff",
        )
        cart_header.pack(
            fill="x",
            padx=20,
            pady=(18, 10),
        )

        tk.Label(
            cart_header,
            text="CART",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(side="left")

        tk.Button(
            cart_header,
            text="Remove Selected",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#dc2626",
            relief="flat",
            cursor="hand2",
            command=self.remove_selected,
        ).pack(side="right")

        table_frame = tk.Frame(
            cart_card,
            bg="#ffffff",
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20),
        )

        columns = (
            "Product",
            "Qty",
            "Price",
            "Total",
        )

        self.cart_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Modern.Treeview",
        )

        self.cart_table.heading("Product", text="Product")
        self.cart_table.heading("Qty", text="Qty")
        self.cart_table.heading("Price", text="Price")
        self.cart_table.heading("Total", text="Total")

        self.cart_table.column(
            "Product",
            width=250,
        )

        self.cart_table.column(
            "Qty",
            width=70,
            anchor="center",
        )

        self.cart_table.column(
            "Price",
            width=100,
            anchor="e",
        )

        self.cart_table.column(
            "Total",
            width=110,
            anchor="e",
        )

        self.cart_table.pack(
            fill="both",
            expand=True,
        )

        # =====================================================
        # RIGHT SIDE - SUMMARY
        # =====================================================

        summary_card = tk.Frame(
            content,
            bg="#ffffff",
            width=285,
        )
        summary_card.pack(
            side="right",
            fill="y",
        )
        summary_card.pack_propagate(False)

        tk.Label(
            summary_card,
            text="BILL SUMMARY",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 20),
        )

        self.subtotal_label = self.create_summary_row(
            summary_card,
            "Subtotal",
            "₹ 0.00",
        )

        self.gst_label = self.create_summary_row(
            summary_card,
            "GST (5%)",
            "₹ 0.00",
        )

        self.discount_label = self.create_summary_row(
            summary_card,
            "Discount",
            "₹ 0.00",
        )

        tk.Frame(
            summary_card,
            bg="#e5e7eb",
            height=1,
        ).pack(
            fill="x",
            padx=20,
            pady=15,
        )

        total_frame = tk.Frame(
            summary_card,
            bg="#ffffff",
        )
        total_frame.pack(
            fill="x",
            padx=20,
        )

        tk.Label(
            total_frame,
            text="TOTAL",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#1f2937",
        ).pack(side="left")

        self.total_label = tk.Label(
            total_frame,
            text="₹ 0.00",
            font=("Segoe UI", 18, "bold"),
            bg="#ffffff",
            fg="#2563eb",
        )
        self.total_label.pack(side="right")

        # Generate QR
        tk.Button(
            summary_card,
            text="Generate Payment QR",
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            pady=12,
            command=self.generate_payment_qr,
        ).pack(
            fill="x",
            padx=20,
            pady=(35, 10),
        )

        # Pay with Razorpay
        tk.Button(
            summary_card,
            text="Pay with Razorpay",
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            pady=10,
            command=self.pay_with_razorpay,
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 10),
        )

        # Save invoice
        tk.Button(
            summary_card,
            text="Save Invoice",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#2563eb",
            activeforeground="#1d4ed8",
            relief="solid",
            bd=1,
            cursor="hand2",
            pady=9,
            command=self.save_current_invoice,
        ).pack(
            fill="x",
            padx=20,
        )

    # =========================================================
    # LOAD CUSTOMERS
    # =========================================================

    def load_customers(self) -> None:
        """Load customers from MySQL."""

        try:
            self.customers = get_all_customers()

            customer_names = [
                customer["customer_name"]
                for customer in self.customers
            ]

            self.customer_combo["values"] = customer_names

            if customer_names:
                self.customer_combo.current(0)

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load customers:\n{error}",
                parent=self.root,
            )

    # =========================================================
    # LOAD PRODUCTS
    # =========================================================

    def load_products(self) -> None:
        """Load products from MySQL."""

        try:
            self.products = get_all_products()

            product_names = [
                product["product_name"]
                for product in self.products
            ]

            self.product_combo["values"] = product_names

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load products:\n{error}",
                parent=self.root,
            )

    # =========================================================
    # PRODUCT SELECTION
    # =========================================================

    def on_product_selected(self, event=None) -> None:
        """Display the selected product price."""

        selected_name = self.product_combo.get()

        for product in self.products:
            if product["product_name"] == selected_name:
                self.price_label.config(
                    text=f"₹ {float(product['price']):.2f}"
                )
                break

    # =========================================================
    # ADD TO CART
    # =========================================================

    def add_to_cart(self) -> None:
        """Add selected product to cart."""

        product_name = self.product_combo.get()
        quantity_text = self.quantity_entry.get().strip()

        if not product_name:
            messagebox.showerror(
                "Product Required",
                "Please select a product.",
                parent=self.root,
            )
            return

        try:
            quantity = int(quantity_text)

            if quantity <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Quantity must be a positive number.",
                parent=self.root,
            )
            return

        selected_product = None

        for product in self.products:
            if product["product_name"] == product_name:
                selected_product = product
                break

        if selected_product is None:
            messagebox.showerror(
                "Product Error",
                "Selected product could not be found.",
                parent=self.root,
            )
            return

        stock = int(selected_product["stock_quantity"])

        # Check stock
        if quantity > stock:
            messagebox.showerror(
                "Insufficient Stock",
                f"Only {stock} units available.",
                parent=self.root,
            )
            return

        price = float(selected_product["price"])
        total = price * quantity

        # Add item to cart
        self.cart.append(
            {
                "product_id": selected_product["product_id"],
                "product_name": selected_product["product_name"],
                "quantity": quantity,
                "price": price,
                "total": total,
            }
        )

        self.refresh_cart()

        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")

    # =========================================================
    # REFRESH CART
    # =========================================================

    def refresh_cart(self) -> None:
        """Refresh cart table and totals."""

        for item in self.cart_table.get_children():
            self.cart_table.delete(item)

        for item in self.cart:
            self.cart_table.insert(
                "",
                tk.END,
                values=(
                    item["product_name"],
                    item["quantity"],
                    f"₹ {item['price']:.2f}",
                    f"₹ {item['total']:.2f}",
                ),
            )

        self.calculate_total()

    # =========================================================
    # REMOVE SELECTED
    # =========================================================

    def remove_selected(self) -> None:
        """Remove selected cart item."""

        selected = self.cart_table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an item from the cart.",
                parent=self.root,
            )
            return

        selected_index = self.cart_table.index(selected[0])

        self.cart.pop(selected_index)

        self.refresh_cart()

    # =========================================================
    # CALCULATE TOTAL
    # =========================================================

    def calculate_total(self) -> None:
        """Calculate subtotal, GST and grand total."""

        subtotal = sum(
            item["total"]
            for item in self.cart
        )

        gst = subtotal * 0.05

        discount = 0.0

        grand_total = (
            subtotal
            + gst
            - discount
        )

        self.subtotal_label.config(
            text=f"₹ {subtotal:.2f}"
        )

        self.gst_label.config(
            text=f"₹ {gst:.2f}"
        )

        self.discount_label.config(
            text=f"₹ {discount:.2f}"
        )

        self.total_label.config(
            text=f"₹ {grand_total:.2f}"
        )

    # =========================================================
    # GENERATE PAYMENT QR
    # =========================================================

    def generate_payment_qr(self) -> None:
        """Generate and display a UPI QR for the saved invoice amount."""

        if self.current_invoice_id is None:
            messagebox.showwarning(
                "Save Invoice First",
                "Please save the invoice before generating the payment QR.",
                parent=self.root,
            )
            return

        subtotal = sum(item["total"] for item in self.cart)
        gst = subtotal * 0.05
        discount = 0.0
        grand_total = subtotal + gst - discount

        if grand_total <= 0:
            messagebox.showerror(
                "Invalid Amount",
                "The invoice amount must be greater than zero.",
                parent=self.root,
            )
            return

        try:
            qr_directory = PROJECT_ROOT / "assets"
            qr_directory.mkdir(parents=True, exist_ok=True)

            qr_path = (
                qr_directory
                / f"invoice_{self.current_invoice_id}_qr.png"
            )

            generate_upi_qr(
                amount=grand_total,
                invoice_id=self.current_invoice_id,
                output_path=str(qr_path),
            )

            qr_window = tk.Toplevel(self.root)
            qr_window.title("Payment QR - SmartInvoice Pro")
            qr_window.geometry("430x560")
            qr_window.resizable(False, False)

            tk.Label(
                qr_window,
                text="Scan to Pay",
                font=("Segoe UI", 18, "bold"),
            ).pack(pady=(20, 5))

            tk.Label(
                qr_window,
                text=f"Invoice: {self.current_invoice_number}",
                font=("Segoe UI", 10),
                fg="#6b7280",
            ).pack(pady=(0, 5))

            tk.Label(
                qr_window,
                text=f"Amount: ₹ {grand_total:.2f}",
                font=("Segoe UI", 14, "bold"),
            ).pack(pady=(0, 15))

            qr_image = Image.open(qr_path)
            qr_image = qr_image.resize(
                (300, 300),
                Image.Resampling.LANCZOS,
            )
            self.qr_image_tk = ImageTk.PhotoImage(qr_image)

            tk.Label(
                qr_window,
                image=self.qr_image_tk,
            ).pack()

            tk.Label(
                qr_window,
                text="UPI payment QR generated from the invoice amount.",
                font=("Segoe UI", 9),
                fg="#6b7280",
            ).pack(pady=15)

        except Exception as error:
            messagebox.showerror(
                "QR Generation Error",
                f"Could not generate payment QR:\n{error}",
                parent=self.root,
            )

    # =========================================================
    # PAY WITH RAZORPAY
    # =========================================================

    def pay_with_razorpay(self) -> None:
        """Create a Razorpay Test Mode order and open Checkout."""

        if self.current_invoice_id is None:
            messagebox.showwarning(
                "Save Invoice First",
                "Please save the invoice before starting a Razorpay payment.",
                parent=self.root,
            )
            return

        # Calculate the same total displayed in the Billing UI.
        subtotal = sum(
            item["total"]
            for item in self.cart
        )

        gst = subtotal * 0.05
        discount = 0.0
        grand_total = subtotal + gst - discount

        if grand_total <= 0:
            messagebox.showerror(
                "Invalid Amount",
                "The invoice amount must be greater than zero.",
                parent=self.root,
            )
            return

        try:
            # Create the Razorpay order and local Pending payment record.
            payment_data = create_payment_order(
                invoice_id=self.current_invoice_id,
                amount=grand_total,
            )

            # Start Flask locally in the background.
            ensure_callback_server_running()

            # Give Flask a moment to start before opening the browser.
            time.sleep(0.5)

            checkout_url = (
                "http://127.0.0.1:5000/checkout?"
                + urlencode(
                    {
                        "order_id": payment_data["razorpay_order_id"],
                        "amount": f"{grand_total:.2f}",
                        "payment_id": payment_data["payment_id"],
                    }
                )
            )

            webbrowser.open(checkout_url)

            messagebox.showinfo(
                "Razorpay Checkout",
                f"Razorpay Checkout has been opened in your browser.\n\n"
                f"Invoice: {self.current_invoice_number}\n"
                f"Amount: ₹ {grand_total:.2f}\n\n"
                f"Complete the payment in Razorpay Test Mode.",
                parent=self.root,
            )

        except Exception as error:
            messagebox.showerror(
                "Razorpay Payment Error",
                f"Could not start Razorpay payment:\n{error}",
                parent=self.root,
            )

    # =========================================================
    # SAVE INVOICE
    # =========================================================

    def save_current_invoice(self) -> None:
        """Save the current cart as an invoice."""

        # Prevent accidental duplicate invoices from the same cart.
        if self.current_invoice_id is not None:
            messagebox.showwarning(
                "Invoice Already Saved",
                f"This cart is already saved as invoice "
                f"{self.current_invoice_number}.",
                parent=self.root,
            )
            return

        # Customer is required.
        selected_customer_name = self.customer_combo.get().strip()

        if not selected_customer_name:
            messagebox.showerror(
                "Customer Required",
                "Please select a customer.",
                parent=self.root,
            )
            return

        # Cart must contain at least one item.
        if not self.cart:
            messagebox.showerror(
                "Empty Cart",
                "Please add at least one product to the cart.",
                parent=self.root,
            )
            return

        # Find the selected customer from the customers loaded from MySQL.
        selected_customer = None

        for customer in self.customers:
            if customer["customer_name"] == selected_customer_name:
                selected_customer = customer
                break

        if selected_customer is None:
            messagebox.showerror(
                "Customer Error",
                "Selected customer could not be found.",
                parent=self.root,
            )
            return

        # Get the currently logged-in user.
        current_user = self.session.get_current_user()

        if current_user is None:
            messagebox.showerror(
                "Authentication Error",
                "No logged-in user found. Please log in again.",
                parent=self.root,
            )
            return

        # Calculate the same totals displayed in the Billing UI.
        subtotal = sum(
            item["total"]
            for item in self.cart
        )

        gst = subtotal * 0.05
        discount = 0.0
        grand_total = subtotal + gst - discount

        try:
            invoice_id, invoice_number = save_invoice(
                customer_id=selected_customer["customer_id"],
                user_id=current_user.user_id,
                grand_total=grand_total,
                cart_items=self.cart,
            )

            # Keep these values for the upcoming QR/payment workflow.
            self.current_invoice_id = invoice_id
            self.current_invoice_number = invoice_number

            # IMPORTANT:
            # parent=self.root keeps the popup attached to
            # the Billing window instead of the Dashboard.
            messagebox.showinfo(
                "Invoice Saved",
                f"Invoice saved successfully!\n\n"
                f"Invoice Number: {invoice_number}\n"
                f"Total: ₹ {grand_total:.2f}\n\n"
                f"Payment Status: Pending",
                parent=self.root,
            )

        except Exception as error:
            messagebox.showerror(
                "Invoice Error",
                f"Could not save invoice:\n{error}",
                parent=self.root,
            )

    # =========================================================
    # SUMMARY ROW
    # =========================================================

    def create_summary_row(
        self,
        parent: tk.Frame,
        title: str,
        value: str,
    ) -> tk.Label:
        """Create one summary row."""

        frame = tk.Frame(
            parent,
            bg="#ffffff",
        )
        frame.pack(
            fill="x",
            padx=20,
            pady=7,
        )

        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(side="left")

        value_label = tk.Label(
            frame,
            text=value,
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#1f2937",
        )
        value_label.pack(side="right")

        return value_label


def create_billing_window(
    parent,
    session: Session,
    back_callback=None,
) -> None:
    """Open the billing screen inside the provided parent."""

    BillingWindow(
        parent,
        session,
        back_callback,
    )