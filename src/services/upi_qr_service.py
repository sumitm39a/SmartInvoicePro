import qrcode

from src.config.settings import get_env


def generate_upi_qr(
    amount: float,
    invoice_id: int,
    output_path: str,
) -> str:
    """
    Generate a UPI QR code containing the invoice amount.

    The QR contains:
        - UPI ID
        - Merchant name
        - Fixed payment amount
        - Invoice reference
    """

    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    upi_id = get_env("UPI_ID")
    upi_name = get_env("UPI_NAME")

    # UPI payment URI.
    upi_uri = (
        f"upi://pay?"
        f"pa={upi_id}"
        f"&pn={upi_name}"
        f"&am={amount:.2f}"
        f"&cu=INR"
        f"&tn=Invoice%20{invoice_id}"
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(upi_uri)
    qr.make(fit=True)

    image = qr.make_image()
    image.save(output_path)

    return output_path