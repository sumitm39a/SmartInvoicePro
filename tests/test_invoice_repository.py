from src.database.invoice_repository import save_invoice


# Existing admin user
user_id = 1

# Existing customer: Priya Verma
customer_id = 2

# Test cart
cart_items = [
    {
        "product_id": 1,
        "quantity": 2,
        "price": 60.00,
        "total": 120.00,
    },
    {
        "product_id": 2,
        "quantity": 1,
        "price": 40.00,
        "total": 40.00,
    },
]

grand_total = 160.00


invoice_id, invoice_number = save_invoice(
    customer_id=customer_id,
    user_id=user_id,
    grand_total=grand_total,
    cart_items=cart_items,
)

print("Invoice saved successfully!")
print("Invoice ID:", invoice_id)
print("Invoice Number:", invoice_number)