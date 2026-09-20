import razorpay

from src.config.settings import get_env


def get_razorpay_client() -> razorpay.Client:
    """
    Create and return a Razorpay client using Test Mode credentials
    stored in the project's .env file.
    """

    key_id = get_env("RAZORPAY_KEY_ID")
    key_secret = get_env("RAZORPAY_KEY_SECRET")

    return razorpay.Client(
        auth=(key_id, key_secret)
    )