import os
from dotenv import load_dotenv

load_dotenv()

MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("PROD_MERCADO_PAGO_ACCESS_TOKEN")

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SECRET_KEY = "SECRET_KEY_WEBSOCKET"
    
    @staticmethod
    def init_app(app):
        pass