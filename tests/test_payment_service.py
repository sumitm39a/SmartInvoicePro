from src.services.payment_service import create_payment_order


result = create_payment_order(
    invoice_id=3,
    amount=1111.95,
)

print("Payment order created successfully!")
print("Razorpay Order ID:", result["razorpay_order_id"])
print("Payment ID:", result["payment_id"])
print("Amount:", result["amount"])
print("Currency:", result["currency"])
print("Receipt:", result["receipt"])