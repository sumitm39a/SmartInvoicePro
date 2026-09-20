from src.database.payment_repository import create_payment


payment_id = create_payment(
    invoice_id=3,
    amount=1111.95,
    payment_method="UPI",
)

print("Payment record created successfully!")
print("Payment ID:", payment_id)