from datetime import datetime

from src.database.connection import create_connection


# =========================================================
# GENERATE INVOICE NUMBER
# =========================================================

def generate_invoice_number() -> str:
    """Generate a unique invoice number based on current date and time."""

    return datetime.now().strftime("INV-%Y%m%d-%H%M%S")


# =========================================================
# SAVE INVOICE
# =========================================================

def save_invoice(
    customer_id: int,
    user_id: int,
    grand_total: float,
    cart_items: list,
) -> tuple[int, str]:
    """
    Save a new invoice and its invoice items.

    Stock is NOT deducted here.
    Stock is deducted only after successful payment verification
    through mark_invoice_paid().
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # ---------------------------------------------------------
        # 1. Generate invoice number
        # ---------------------------------------------------------

        invoice_number = generate_invoice_number()

        # ---------------------------------------------------------
        # 2. Save invoice
        # ---------------------------------------------------------

        invoice_query = """
            INSERT INTO invoices
            (
                invoice_number,
                customer_id,
                user_id,
                grand_total,
                payment_status
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            invoice_query,
            (
                invoice_number,
                customer_id,
                user_id,
                grand_total,
                "Pending",
            ),
        )

        invoice_id = cursor.lastrowid

        # ---------------------------------------------------------
        # 3. Save invoice items
        # ---------------------------------------------------------

        item_query = """
            INSERT INTO invoice_items
            (
                invoice_id,
                product_id,
                quantity,
                price_at_sale,
                subtotal
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        for item in cart_items:
            cursor.execute(
                item_query,
                (
                    invoice_id,
                    item["product_id"],
                    item["quantity"],
                    item["price"],
                    item["total"],
                ),
            )

        # ---------------------------------------------------------
        # 4. Commit
        # ---------------------------------------------------------

        connection.commit()

        return invoice_id, invoice_number

    except Exception:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# =========================================================
# MARK INVOICE PAID
# =========================================================

def mark_invoice_paid(invoice_id: int) -> None:
    """
    Mark an invoice as paid after successful payment verification
    and deduct the purchased quantities from product stock.

    Stock is deducted only once.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # ---------------------------------------------------------
        # 1. Lock the invoice row
        # ---------------------------------------------------------

        invoice_query = """
            SELECT
                invoice_id,
                payment_status
            FROM invoices
            WHERE invoice_id = %s
            FOR UPDATE
        """

        cursor.execute(
            invoice_query,
            (invoice_id,),
        )

        invoice = cursor.fetchone()

        if invoice is None:
            raise ValueError(
                "The selected invoice does not exist."
            )

        # ---------------------------------------------------------
        # 2. Prevent duplicate stock deduction
        # ---------------------------------------------------------

        if invoice["payment_status"] == "Paid":
            connection.commit()
            return

        # ---------------------------------------------------------
        # 3. Get invoice items
        # ---------------------------------------------------------

        items_query = """
            SELECT
                product_id,
                quantity
            FROM invoice_items
            WHERE invoice_id = %s
        """

        cursor.execute(
            items_query,
            (invoice_id,),
        )

        items = cursor.fetchall()

        if not items:
            raise ValueError(
                "The invoice does not contain any products."
            )

        # ---------------------------------------------------------
        # 4. Deduct stock
        # ---------------------------------------------------------

        stock_query = """
            UPDATE products
            SET
                stock_quantity = stock_quantity - %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = %s
              AND stock_quantity >= %s
        """

        for item in items:

            quantity = int(item["quantity"])
            product_id = int(item["product_id"])

            cursor.execute(
                stock_query,
                (
                    quantity,
                    product_id,
                    quantity,
                ),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    f"Insufficient stock for product ID {product_id}."
                )

        # ---------------------------------------------------------
        # 5. Mark invoice as Paid
        # ---------------------------------------------------------

        update_invoice_query = """
            UPDATE invoices
            SET payment_status = %s
            WHERE invoice_id = %s
        """

        cursor.execute(
            update_invoice_query,
            (
                "Paid",
                invoice_id,
            ),
        )

        # ---------------------------------------------------------
        # 6. Commit stock + invoice together
        # ---------------------------------------------------------

        connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# =========================================================
# GET ALL INVOICES
# =========================================================

def get_all_invoices() -> list:
    """Return all invoices with customer information."""

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                i.invoice_id,
                i.invoice_number,
                i.customer_id,
                c.customer_name,
                i.user_id,
                i.invoice_date,
                i.grand_total,
                i.payment_status,
                i.remarks
            FROM invoices i
            LEFT JOIN customers c
                ON i.customer_id = c.customer_id
            ORDER BY i.invoice_id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# =========================================================
# GET INVOICE ITEMS
# =========================================================

def get_invoice_items(invoice_id: int) -> list:
    """Return all products belonging to an invoice."""

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                ii.invoice_item_id,
                ii.invoice_id,
                ii.product_id,
                p.product_name,
                ii.quantity,
                ii.price_at_sale,
                ii.subtotal
            FROM invoice_items ii
            LEFT JOIN products p
                ON ii.product_id = p.product_id
            WHERE ii.invoice_id = %s
            ORDER BY ii.invoice_item_id
        """

        cursor.execute(
            query,
            (invoice_id,),
        )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()