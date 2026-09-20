from src.services.payment_service import create_payment_qr


result = create_payment_qr(
    invoice_id=3,
    amount=1111.95,
    payment_id=2,
)

print("Razorpay QR created successfully!")
print("QR Code ID:", result["qr_code_id"])
print("Image URL:", result["image_url"])
print("Amount:", result["amount"])
print("Invoice ID:", result["invoice_id"])
print("Payment ID:", result["payment_id"])
print("Status:", result["status"])