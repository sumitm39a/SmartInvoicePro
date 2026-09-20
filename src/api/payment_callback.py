import hmac
import hashlib
import json
from flask import Flask, request, jsonify, Response

from src.config.settings import get_env

from src.database.payment_repository import (
    update_payment_success,
    get_payment_invoice_id,
    create_payment_verification,
)
from src.database.invoice_repository import mark_invoice_paid


app = Flask(__name__)


def verify_razorpay_signature(
    order_id: str,
    payment_id: str,
    signature: str,
) -> bool:
    """
    Verify Razorpay Checkout's payment signature.

    The Razorpay Key Secret stays on the Python/backend side
    and is never exposed to the browser.
    """

    key_secret = get_env("RAZORPAY_KEY_SECRET")

    message = f"{order_id}|{payment_id}"

    expected_signature = hmac.new(
        key_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


@app.route("/checkout", methods=["GET"])
def checkout():
    """
    Display a Razorpay Checkout page.

    Only the Razorpay Key ID is sent to the browser.
    The Key Secret remains inside the Python application.
    """

    key_id = get_env("RAZORPAY_KEY_ID")
    order_id = request.args.get("order_id")
    amount = request.args.get("amount")
    payment_id = request.args.get("payment_id")

    if not all([key_id, order_id, amount, payment_id]):
        return Response(
            "Missing checkout information.",
            status=400,
            mimetype="text/plain",
        )

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartInvoice Pro - Razorpay Payment</title>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>

    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}

        .card {{
            background: white;
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.10);
            text-align: center;
            width: 350px;
        }}

        h2 {{
            margin-bottom: 10px;
        }}

        .amount {{
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
        }}

        button {{
            border: none;
            background: #2563eb;
            color: white;
            padding: 13px 30px;
            border-radius: 7px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
        }}

        button:hover {{
            background: #1d4ed8;
        }}

        .note {{
            margin-top: 20px;
            color: #6b7280;
            font-size: 12px;
        }}
    </style>
</head>

<body>

<div class="card">
    <h2>SmartInvoice Pro</h2>
    <div>Razorpay Test Payment</div>

    <div class="amount">
        ₹ {amount}
    </div>

    <button onclick="startPayment()">
        Pay Now
    </button>

    <div class="note">
        This payment uses Razorpay Test Mode.
    </div>
</div>

<script>
function startPayment() {{

    var options = {{
        "key": "{key_id}",
        "amount": Math.round(parseFloat("{amount}") * 100),
        "currency": "INR",
        "name": "SmartInvoice Pro",
        "description": "Invoice Payment",
        "order_id": "{order_id}",

        

        "handler": function (response) {{

            fetch("/payment-success", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},

                body: JSON.stringify({{
                    "razorpay_payment_id": response.razorpay_payment_id,
                    "razorpay_order_id": response.razorpay_order_id,
                    "razorpay_signature": response.razorpay_signature,
                    "payment_id": "{payment_id}"
                }})
            }})
            .then(function(response) {{
                return response.json();
            }})
            .then(function(result) {{

                if (result.success) {{
                    document.body.innerHTML = `
                        <div class="card">
                            <h2>Payment Successful</h2>
                            <div>Payment verified successfully.</div>
                            <div class="amount">₹ {amount}</div>
                            <div class="note">
                                You can close this window now.
                            </div>
                        </div>
                    `;
                }} else {{
                    alert("Payment verification failed: " + result.message);
                }}

            }})
            .catch(function(error) {{
                alert("Could not contact the SmartInvoice payment server.");
                console.error(error);
            }});
        }},

        "theme": {{
            "color": "#2563eb"
        }}
    }};

    var razorpay = new Razorpay(options);

    razorpay.on("payment.failed", function(response) {{
        alert(
            "Payment failed.\\n\\n" +
            "Reason: " +
            response.error.description
        );
    }});

    razorpay.open();
}}
</script>

</body>
</html>
"""

    return Response(
        html,
        status=200,
        mimetype="text/html",
    )


@app.route("/payment-success", methods=["POST"])
def payment_success():
    """
    Receive and verify a successful Razorpay Checkout response.
    """

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No payment data received.",
        }), 400

    order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")
    local_payment_id = data.get("payment_id")

    if not all([
        order_id,
        razorpay_payment_id,
        signature,
        local_payment_id,
    ]):
        return jsonify({
            "success": False,
            "message": "Incomplete payment response.",
        }), 400

    try:
        local_payment_id = int(local_payment_id)

        # ---------------------------------------------------------
        # 1. Verify Razorpay signature
        # ---------------------------------------------------------
        is_valid = verify_razorpay_signature(
            order_id=order_id,
            payment_id=razorpay_payment_id,
            signature=signature,
        )

        if not is_valid:
            return jsonify({
                "success": False,
                "message": "Invalid Razorpay signature.",
            }), 400

        # ---------------------------------------------------------
        # 2. Find invoice associated with local payment
        # ---------------------------------------------------------
        invoice_id = get_payment_invoice_id(
            payment_id=local_payment_id,
        )

        # ---------------------------------------------------------
        # 3. Mark payment as successful
        # ---------------------------------------------------------
        update_payment_success(
            payment_id=local_payment_id,
            transaction_id=razorpay_payment_id,
        )
                # ---------------------------------------------------------
        # 3A. Store payment verification details
        # ---------------------------------------------------------
        create_payment_verification(
            payment_id=local_payment_id,
            provider="Razorpay",
            external_reference=razorpay_payment_id,
            verification_status="Success",
            api_response=json.dumps({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "signature_verified": True,
            }),
        )

        # ---------------------------------------------------------
        # 4. Mark invoice as paid
        # ---------------------------------------------------------
        mark_invoice_paid(
            invoice_id=invoice_id,
        )

        return jsonify({
            "success": True,
            "message": "Payment verified successfully.",
            "payment_id": local_payment_id,
            "invoice_id": invoice_id,
        })

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error),
        }), 404

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error),
        }), 500


def start_callback_server() -> None:
    """
    Start the local payment callback server.
    """

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
    )

