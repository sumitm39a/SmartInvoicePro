from src.database.connection import create_connection


def add_product(
    category_id: int,
    name: str,
    description: str | None,
    price: float,
    stock_quantity: int,
) -> None:
    """Add a new product to the database."""

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Prevent duplicate product names.
        check_query = """
            SELECT product_id
            FROM products
            WHERE LOWER(product_name) = LOWER(%s)
            LIMIT 1
        """

        cursor.execute(check_query, (name.strip(),))

        if cursor.fetchone() is not None:
            raise ValueError(
                "A product with this name already exists."
            )

        query = """
            INSERT INTO products (
                product_name,
                category_id,
                price,
                stock_quantity,
                description
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                name.strip(),
                category_id,
                price,
                stock_quantity,
                description,
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


def get_all_products():
    """Return all products."""

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                p.product_id,
                p.product_name,
                c.category_name,
                p.category_id,
                p.price,
                p.stock_quantity,
                p.barcode,
                p.description
            FROM products p
            LEFT JOIN categories c
                ON p.category_id = c.category_id
            ORDER BY p.product_id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_categories():
    """Return all product categories."""

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                category_id,
                category_name
            FROM categories
            ORDER BY category_name
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def delete_product(product_id: int) -> None:
    """
    Delete a product only if it has never been used in an invoice.

    Historical invoice items must remain valid, so products already
    used in invoice history cannot be physically deleted.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Check invoice history first.
        check_query = """
            SELECT 1
            FROM invoice_items
            WHERE product_id = %s
            LIMIT 1
        """

        cursor.execute(
            check_query,
            (product_id,),
        )

        if cursor.fetchone() is not None:
            raise ValueError(
                "This product cannot be deleted because it "
                "has already been used in an invoice."
            )

        delete_query = """
            DELETE FROM products
            WHERE product_id = %s
        """

        cursor.execute(
            delete_query,
            (product_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "The selected product no longer exists."
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


def update_product(
    product_id: int,
    category_id: int,
    name: str,
    price: float,
    stock_quantity: int,
) -> None:
    """Update an existing product."""

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Prevent duplicate names belonging to another product.
        check_query = """
            SELECT product_id
            FROM products
            WHERE LOWER(product_name) = LOWER(%s)
              AND product_id <> %s
            LIMIT 1
        """

        cursor.execute(
            check_query,
            (
                name.strip(),
                product_id,
            ),
        )

        if cursor.fetchone() is not None:
            raise ValueError(
                "Another product with this name already exists."
            )

        query = """
            UPDATE products
            SET
                product_name = %s,
                category_id = %s,
                price = %s,
                stock_quantity = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = %s
        """

        cursor.execute(
            query,
            (
                name.strip(),
                category_id,
                price,
                stock_quantity,
                product_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "The selected product no longer exists."
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