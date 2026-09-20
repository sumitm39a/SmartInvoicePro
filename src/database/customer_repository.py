from src.database.connection import create_connection


def add_customer(
    name: str,
    mobile_number: str | None,
    email: str | None,
    address: str | None,
) -> None:
    """Add a new customer to the database."""

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Prevent duplicate mobile numbers.
        if mobile_number:
            check_query = """
                SELECT customer_id
                FROM customers
                WHERE mobile_number = %s
                LIMIT 1
            """

            cursor.execute(
                check_query,
                (mobile_number,),
            )

            if cursor.fetchone() is not None:
                raise ValueError(
                    "A customer with this mobile number already exists."
                )

        query = """
            INSERT INTO customers (
                customer_name,
                mobile_number,
                email,
                address
            )
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                name.strip(),
                mobile_number,
                email,
                address,
            ),
        )

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


def get_all_customers():
    """Return all customers from the database."""

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                customer_id,
                customer_name,
                mobile_number,
                email,
                address,
                loyalty_points
            FROM customers
            ORDER BY customer_id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def delete_customer(customer_id: int) -> None:
    """
    Delete a customer only if they have never been used
    in an invoice.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        check_query = """
            SELECT 1
            FROM invoices
            WHERE customer_id = %s
            LIMIT 1
        """

        cursor.execute(
            check_query,
            (customer_id,),
        )

        if cursor.fetchone() is not None:
            raise ValueError(
                "This customer cannot be deleted because "
                "they already have invoice history."
            )

        delete_query = """
            DELETE FROM customers
            WHERE customer_id = %s
        """

        cursor.execute(
            delete_query,
            (customer_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "The selected customer no longer exists."
            )

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