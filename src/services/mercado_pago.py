import uuid
import mercadopago

from config import MERCADO_PAGO_ACCESS_TOKEN
from src.errors.error_types.http_mercado_pago import HttpMercadoPagoError

class MercadoPago:
    def __init__(self) -> None:
        self.__sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)
        self.__request_options = mercadopago.config.RequestOptions()

        self.__request_options.custom_headers = {
            "x-idempotency-key": str(uuid.uuid4())
        }

    def create_pix_payment(self, value: float, email: str):
        payment_data = {
            "transaction_amount": float(value),
            "description": "some description here",
            "payment_method_id": "pix",
            "payer": {
                "email": email
            }
        }

        payment_response = self.__sdk.payment().create(payment_data, self.__request_options)

        if payment_response["status"] not in [200, 201, 204]:
            raise HttpMercadoPagoError(
            payment_response['response']['message'], payment_response["status"])

        response = {
            "bank_payment_id": payment_response.get("response", {}).get("id"),
            "qr_code_base64": payment_response.get("response", {}).get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code_base64")
        }

        return response