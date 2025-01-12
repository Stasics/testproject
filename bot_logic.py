from flask import Flask, request, jsonify
import logging
import uuid
import redis
import os
import json
import requests

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Подключение к Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Настройки модуля авторизации
AUTH_MODULE_URL = os.getenv("AUTH_MODULE_URL", "http://localhost:8081/auth")


@app.route('/', methods=['POST'])
def bot_logic():
    logger.info("Bot logic: got request")
    data = request.get_json()
    logger.debug(f"Bot Logic: Received {data}")

    if not data:
        return jsonify({"message": "No JSON data received"}), 400

    command = data.get("command")
    chat_id = str(data.get("chat_id"))
    user_data = redis_client.get(chat_id)

    if user_data:
        user_data = json.loads(user_data)
    logger.debug(f"Bot Logic: User {user_data}")

    if not command:
        return jsonify({"message": "No command received"}), 400

    if command == "/login":
        if not data.get("data") or not data.get("data").get("type"):
            if user_data and user_data.get("status") != "anonymous":
                return jsonify({"message": "Вы уже авторизованы"}), 200
            return jsonify({"message": "Выберите способ авторизации: GitHub, Яндекс ID, код"}), 200
        login_type = data.get("data").get("type")
        token = str(uuid.uuid4())
        redis_client.set(chat_id, json.dumps({"status": "anonymous", "token": token, "login_type": login_type}))

        # Запрос в модуль авторизации
        try:
            auth_response = requests.post(AUTH_MODULE_URL, json={"token": token})
            auth_response.raise_for_status()
            auth_result = auth_response.json()
            logger.debug(f"Bot logic: Auth result: {auth_result}")
            if auth_result["status"] == "success":
                # Сохраняем access и refresh токены
                access_token = str(uuid.uuid4())  # Заглушка, надо будет использовать JWT
                refresh_token = str(uuid.uuid4())  # Заглушка, надо будет использовать JWT
                redis_client.set(chat_id, json.dumps(
                    {"status": "authorized", "token": token, "login_type": login_type, "access_token": access_token,
                     "refresh_token": refresh_token}))
                return jsonify({"message": f"Вы авторизовались с помощью {login_type}, user: {auth_result['user']}"})
            elif auth_result["status"] == "unauthorized":
                redis_client.delete(chat_id)
                return jsonify({"message": f"Неудачная авторизация"})
            elif auth_result["status"] == "invalid token":
                redis_client.delete(chat_id)
                return jsonify({"message": f"Время действия токена истекло"})
            else:
                return jsonify({"message": f"Ошибка авторизации"})
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе авторизации: {e}")
            return jsonify({"message": f"Ошибка при запросе авторизации: {e}"})
    elif not user_data:
        return jsonify({"message": "Вы не авторизованы, напишите /login"}), 200
    elif command == "/tests":
        return jsonify({"message": "Список доступных тестов"}), 200
    elif command == "/test_info":
        return jsonify({"message": "Детали теста"}), 200
    elif command == "/start_test":
        return jsonify({"message": "Начинаем тест"}), 200
    elif command == "/answer":
        return jsonify({"message": "Отвечаем на вопрос"}), 200
    elif command == "/results":
        return jsonify({"message": "Результаты теста"}), 200
    elif command == "/logout":
        redis_client.delete(chat_id)
        return jsonify({"message": "Вы вышли из системы"}), 200
    else:
        return jsonify({"message": "Команда не найдена"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)