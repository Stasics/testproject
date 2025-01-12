import telegram
import asyncio
import logging
import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import bot_config

# Настройки логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)



class TelegramClient:
    def __init__(self, bot_token, bot_url):
        self.bot_token = bot_token
        self.bot_url = bot_url
        self.bot = telegram.Bot(token=bot_token)
        self.last_update_id = 0

    async def get_new_messages(self):
        try:
            updates = await self.bot.get_updates(offset=self.last_update_id, timeout=30)
            if updates:
                self.last_update_id = updates[-1].update_id + 1
            return updates
        except telegram.error.TelegramError as e:
            logger.error(f"Ошибка при получении обновлений: {e}")
            return []

    async def process_message(self, message):
        try:
            chat_id = message.message.chat_id
            text = message.message.text
            logger.info(f"Получено сообщение от {chat_id}: {text}")

            if text == "/help":
                 await self.help_command(message)
                 return

            if text in ["/start", "привет"]:
                await self.send_message(chat_id, "Привет!Я-бот для тестирования.Чтобы получить список доступных команд нажми /help")
                return

            parts = text.split(" ")
            command = parts[0]
            data = {}

            if command == "/login":
                 if len(parts) > 1 and parts[1].startswith("type:"):
                    data["type"] = parts[1].split(":")[1]
                    await self.send_to_bot_logic(chat_id, {"command": command, "data": data})
                 else:
                     await self.send_to_bot_logic(chat_id, {"command": command})
            elif command in ["/tests", "/test_info", "/start_test", "/answer", "/results", "/logout"]:
                await self.send_to_bot_logic(chat_id, {"command": command, "data": data})
            else:
               await self.send_message(chat_id, "Нет такой команды")

        except Exception as e:
          logger.error(f"Ошибка обработки сообщения: {e}")


    async def send_to_bot_logic(self, chat_id, data):
         logger.debug(f"Отправка запроса на: {self.bot_url}, данные: {data}")
         data['chat_id'] = chat_id
         try:
             response = requests.post(self.bot_url, json=data)
             response.raise_for_status()
             if response.status_code == 200:
                await self.send_message(chat_id, response.json()['message'])
             else:
                 await self.send_message(chat_id, "Ошибка при обработке запроса")
         except requests.exceptions.RequestException as e:
           logger.error(f"Ошибка при отправке в Bot Logic: {e}")
           await self.send_message(chat_id, f"Ошибка связи с сервером: {e}")

    async def help_command(self, message):
        help_text = """
        <b>Доступные команды:</b>
        /start - Начать работу с ботом
        /login - Авторизоваться в боте
        /tests - Показать список тестов
        /test_info - Показать детали теста
        /start_test - Начать попытку теста
        /answer - Ответить на вопрос
        /results - Показать результаты теста
        /logout - Выйти из системы
        /help - Получить список команд
        """

        keyboard = [
           ["/start", "/login"],
           ["/tests", "/test_info"],
           ["/start_test", "/answer"],
           ["/results", "/help", "/logout"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await self.send_message(message.message.chat_id, help_text, reply_markup=reply_markup, parse_mode="HTML")


    async def send_message(self, chat_id, message, reply_markup=None, parse_mode=None):
        try:
            await self.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup, parse_mode=parse_mode)
            logger.info(f"Отправлено сообщение пользователю {chat_id}: {message}")
        except telegram.error.TelegramError as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")

    async def run(self):
        while True:
            messages = await self.get_new_messages()
            for message in messages:
                if message:
                    await self.process_message(message)
            await asyncio.sleep(1)

async def main():
    client = TelegramClient(bot_config.TELEGRAM_BOT_TOKEN, bot_config.BOT_URL)
    await client.run()

if __name__ == '__main__':
    asyncio.run(main())