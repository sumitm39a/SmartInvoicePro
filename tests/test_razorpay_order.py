from src.services.payment_service import create_payment_order


invoice_id = 3
amount = 1111.95

order = create_payment_order(
    invoice_id=invoice_id,
    amount=amount,
)

print("Razorpay order created successfully!")
print("Order ID:", order["id"])
print("Amount:", order["amount"])
print("Currency:", order["currency"])
print("Receipt:", order["receipt"])