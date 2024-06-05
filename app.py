from datetime import datetime, timedelta, timezone
import logging

from flask import Flask, jsonify, request, send_file, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

from src.errors.error_types.http_mercado_pago import HttpMercadoPagoError
from src.repository.database import db
from src.models.payment import Payment
from config import Config
from src.services.mercado_pago import MercadoPago
from src.utils.mercado_pago import MercadoPagoUtils
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, supports_credentials=True)
Migrate(app, db)


@app.route("/payments/pix", methods=["POST"])
def create_payment_pix():
    try:
        data = request.get_json()

        if "value" not in data:
            return jsonify({"message": "Invalid value"}), 400
        
        if "email" not in data:
            return jsonify({"message": "Invalid email"}), 400
        
        value = data["value"]
        email = data["email"]
        
        expiration_date = datetime.now(timezone.utc) + timedelta(minutes=30)

        mp = MercadoPago()

        payment_response = mp.create_pix_payment(value, email)

        new_payment = Payment(
            value=value, 
            expiration_date=expiration_date,
            bank_payment_id=payment_response["bank_payment_id"],
            qr_code=payment_response["qr_code_base64"]
        )
        
        db.session.add(new_payment)
        db.session.commit()

        return jsonify({"message": "The payment has been created.", "payment_id": new_payment.id})
    
    except HttpMercadoPagoError as exc:
        return {"error": exc.message}, exc.status_code
    
    except Exception as exc:
        db.session.rollback()
        return {"error": "Ocorreu um erro ao criar o pagamento! Tente novamente mais tarde."}, 500


@app.route("/payments/pix/qr_code/<file_name>", methods=["GET"])
def get_image(file_name: str):
    return send_file(f"static/img/{file_name}.png", mimetype="image/png")


@app.route("/payments/pix/confirmation", methods=["POST"])
def pix_confirmation():
    if not MercadoPagoUtils.validate_signature(request):
        return jsonify({"message": "Invalid signature"}), 400
    
    data = request.get_json()

    if data.get("action") != "payment.update":
        return {}, 200
    
    payment = db.session.execute(db.select(Payment).filter_by(bank_payment_id=data.get("data", {}).get("id"))).scalar_one_or_none()

    if not payment or payment.paid:
        logging.error({
            "error":"Pagamento não encontrado!",
            "request": data
        })
        return {}, 200
    

    payment.paid = True
    db.session.commit()

    socketio.emit(f"payment-confirmed-{payment.id}")

    return {}, 200


@app.route("/payments/pix/<int:payment_id>", methods=["GET"])
def payment_pix_page(payment_id: int):
    payment = db.session.execute(db.select(Payment).filter_by(id=payment_id)).scalar_one_or_none()

    if payment is None:
        return render_template("404.html")

    if payment.paid:
        return render_template("confirmed_payment.html",
                               payment_id=payment.id, 
                               value=payment.value)
    
    return render_template("payment.html", 
                           payment_id=payment.id, 
                           value=payment.value, 
                           host="https://f21c-177-91-141-153.ngrok-free.app",
                           qr_code=payment.qr_code)


@socketio.on("connect")
def handle_connect():
    print("Client Connected to the server")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client has disconnected to the server")


if __name__ == "__main__":
    socketio.run(app)