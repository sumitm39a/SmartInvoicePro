from src.database.connection import create_connection


def get_sales_summary() -> dict:
    """
    Get overall sales statistics from invoices.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                COUNT(*) AS total_invoices,
                COALESCE(SUM(grand_total), 0) AS total_sales,
                SUM(CASE WHEN payment_status = 'Paid' THEN 1 ELSE 0 END)
                    AS paid_invoices,
                SUM(CASE WHEN payment_status = 'Pending' THEN 1 ELSE 0 END)
                    AS pending_invoices,
                SUM(CASE WHEN payment_status = 'Failed' THEN 1 ELSE 0 END)
                    AS failed_invoices
            FROM invoices
        """

        cursor.execute(query)
        result = cursor.fetchone()

        return result

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_product_sales_report() -> list:
    """
    Get quantity sold and sales amount for each product.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                p.product_id,
                p.product_name,
                COALESCE(SUM(ii.quantity), 0) AS quantity_sold,
                COALESCE(SUM(ii.subtotal), 0) AS sales_amount
            FROM products p
            LEFT JOIN invoice_items ii
                ON p.product_id = ii.product_id
            GROUP BY
                p.product_id,
                p.product_name
            ORDER BY sales_amount DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_payment_summary() -> list:
    """
    Get payment count and amount grouped by payment method.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                payment_method,
                COUNT(*) AS payment_count,
                COALESCE(SUM(amount), 0) AS total_amount,
                SUM(
                    CASE
                        WHEN payment_status = 'Success' THEN 1
                        ELSE 0
                    END
                ) AS successful_payments,
                SUM(
                    CASE
                        WHEN payment_status = 'Failed' THEN 1
                        ELSE 0
                    END
                ) AS failed_payments
            FROM payments
            GROUP BY payment_method
            ORDER BY payment_method
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_date_wise_sales_report() -> list:
    """
    Get invoice count and sales amount grouped by date.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                DATE(invoice_date) AS sale_date,
                COUNT(*) AS invoice_count,
                COALESCE(SUM(grand_total), 0) AS total_sales
            FROM invoices
            GROUP BY DATE(invoice_date)
            ORDER BY sale_date DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()