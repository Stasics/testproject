from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.route('/auth', methods=['POST'])
def auth():
    logger.info("Auth module: got request")
    data = request.get_json()
    logger.debug(f"Auth module: Received {data}")

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    token = data.get("token")

    if not token:
        return jsonify({"status": "error", "message": "No token received"}), 400

    # Логика проверки токена (заглушка, токен всегда валидный)
    logger.info(f"Auth Module: Trying to authenticate with token: {token}")

    return jsonify({"status": "success", "user": "test_user"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)