import multiprocessing
import os
import subprocess
import time
import logging
import signal

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_telegram_client():
    try:
        logger.info("Запуск telegram_client.py")
        subprocess.run(["python", "telegram_client.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка запуска telegram_client.py: {e}")


def run_bot_logic():
    try:
        logger.info("Запуск bot_logic.py")
        subprocess.run(["python", "bot_logic.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка запуска bot_logic.py: {e}")


def run_auth_module():
    try:
        logger.info("Запуск auth_module.py")
        subprocess.run(["python", "auth_module.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка запуска auth_module.py: {e}")


def signal_handler(sig, frame):
    logger.info("Получен сигнал остановки, завершаю процессы...")
    for p in processes:
        if p.is_alive():
            p.terminate()
        p.join()
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    processes = []

    # Запускаем процессы
    p1 = multiprocessing.Process(target=run_telegram_client)
    processes.append(p1)
    p1.start()

    p2 = multiprocessing.Process(target=run_bot_logic)
    processes.append(p2)
    p2.start()

    p3 = multiprocessing.Process(target=run_auth_module)
    processes.append(p3)
    p3.start()

    for p in processes:
        p.join()