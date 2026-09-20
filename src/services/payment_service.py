from src.api.razorpay_client import get_razorpay_client
from src.database.payment_repository import create_payment


def create_payment_order(invoice_id: int, amount: float) -> dict:
    """
    Create a Razorpay Test Mode order and a local pending payment record.

    Returns:
        dict containing:
            razorpay_order_id
            payment_id
            amount
            currency
            receipt
    """

    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    amount_in_paise = int(round(amount * 100))

    client = get_razorpay_client()

    order_data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"invoice_{invoice_id}",
        "notes": {
            "invoice_id": str(invoice_id),
        },
    }

    order = client.order.create(data=order_data)

    payment_id = create_payment(
        invoice_id=invoice_id,
        amount=amount,
        payment_method="UPI",
    )

    return {
        "razorpay_order_id": order["id"],
        "payment_id": payment_id,
        "amount": amount,
        "currency": order["currency"],
        "receipt": order["receipt"],
    }
def create_payment_qr(
    invoice_id: int,
    amount: float,
    payment_id: int,
) -> dict:
    """
    Create a Razorpay UPI QR code for an invoice payment.

    The QR is created in Razorpay Test Mode and is configured
    for a single use with a fixed payment amount.
    """

    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    amount_in_paise = int(round(amount * 100))

    client = get_razorpay_client()

    qr_data = {
        "type": "upi_qr",
        "name": f"SmartInvoice Invoice {invoice_id}",
        "usage": "single_use",
        "fixed_amount": True,
        "payment_amount": amount_in_paise,
        "description": f"Payment for Invoice {invoice_id}",
        "notes": {
            "invoice_id": str(invoice_id),
            "payment_id": str(payment_id),
        },
    }

    qr_code = client.qrcode.create(data=qr_data)

    return {
        "qr_code_id": qr_code["id"],
        "image_url": qr_code.get("image_url"),
        "amount": amount,
        "invoice_id": invoice_id,
        "payment_id": payment_id,
        "status": qr_code.get("status"),
    }
