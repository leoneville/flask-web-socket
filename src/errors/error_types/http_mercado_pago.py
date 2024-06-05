class HttpMercadoPagoError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.name = "MercadoPagoError"
        self.status_code = status_code