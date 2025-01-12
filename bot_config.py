import os

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7474301026:AAGuQceNzEaooCT1piBMDlg0BWzxoIRl0gU")

# Bot Logic URL
BOT_URL = os.getenv("BOT_URL", "http://localhost:8080")

# Authorization Module URL
AUTH_MODULE_URL = os.getenv("AUTH_MODULE_URL", "http://localhost:8080/auth")

# Redis Host
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# Redis Port
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
