from src.database.connection import create_connection


def create_payment(
    invoice_id: int,
    amount: float,
    payment_method: str = "UPI",
) -> int:
    """
    Create a pending payment record for an invoice.

    Returns:
        int: Newly created payment_id
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        query = """
            INSERT INTO payments (
                invoice_id,
                payment_method,
                amount,
                payment_status
            )
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                invoice_id,
                payment_method,
                amount,
                "Pending",
            ),
        )

        connection.commit()

        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def update_payment_success(
    payment_id: int,
    transaction_id: str,
) -> None:
    """
    Mark a payment as successfully completed.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        query = """
            UPDATE payments
            SET
                transaction_id = %s,
                payment_status = %s
            WHERE payment_id = %s
        """

        cursor.execute(
            query,
            (
                transaction_id,
                "Success",
                payment_id,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def update_payment_failed(
    payment_id: int,
    transaction_id: str | None = None,
) -> None:
    """
    Mark a payment as failed.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        query = """
            UPDATE payments
            SET
                transaction_id = %s,
                payment_status = %s
            WHERE payment_id = %s
        """

        cursor.execute(
            query,
            (
                transaction_id,
                "Failed",
                payment_id,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

def get_payment_invoice_id(payment_id: int) -> int:
    """
    Get the invoice ID associated with a payment.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        query = """
            SELECT invoice_id
            FROM payments
            WHERE payment_id = %s
        """

        cursor.execute(query, (payment_id,))

        result = cursor.fetchone()

        if result is None:
            raise ValueError(
                f"Payment not found: payment_id={payment_id}"
            )

        return int(result[0])

    finally:
        cursor.close()
        connection.close()

def create_payment_verification(
    payment_id: int,
    provider: str,
    external_reference: str,
    verification_status: str,
    api_response: str,
) -> int:
    """
    Store the result of a payment provider verification.

    Returns:
        int: Newly created verification_id
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        query = """
            INSERT INTO payment_verifications (
                payment_id,
                provider,
                external_reference,
                verification_status,
                api_response,
                verified_at
            )
            VALUES (%s, %s, %s, %s, %s, NOW())
        """

        cursor.execute(
            query,
            (
                payment_id,
                provider,
                external_reference,
                verification_status,
                api_response,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
def get_all_payments() -> list:
    """
    Get all payments with their related invoice number.
    Newest payments are shown first.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                p.payment_id,
                p.invoice_id,
                i.invoice_number,
                p.payment_method,
                p.transaction_id,
                p.amount,
                p.payment_status,
                p.payment_time
            FROM payments p
            INNER JOIN invoices i
                ON p.invoice_id = i.invoice_id
            ORDER BY p.payment_id DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()