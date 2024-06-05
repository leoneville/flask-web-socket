import hashlib
import hmac
import urllib.parse

from config import MERCADO_PAGO_SECRET_KEY


class MercadoPagoUtils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def validate_signature(request) -> bool:
        x_signature = request.headers.get("x-signature")
        x_request_id = request.headers.get("x-request-id")

        parsed_url = urllib.parse.urlparse(request.url)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        data_id = query_params.get("data.id", [""])[0]

        parts = x_signature.split(",")

        ts = None
        hash = None

        for part in parts:
            key_value = part.split("=", 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "ts":
                    ts = value
                elif key == "v1":
                    hash = value

        secret = MERCADO_PAGO_SECRET_KEY

        manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"

        hmac_obj = hmac.new(secret.encode(), msg=manifest.encode(), digestmod=hashlib.sha256)

        sha = hmac_obj.hexdigest()
        if sha == hash:
            return True
        return False