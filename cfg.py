import yaml
import json
import os

PATH_USER_ROOT = os.path.expanduser("~") 
PATH_PAY_BOT_ROOT = f"{PATH_USER_ROOT}/.tg_pay_bot"
PATH_CFG_FILE = f"{PATH_PAY_BOT_ROOT}/config.yml"
PATH_ITEMS_FILE = f"{PATH_PAY_BOT_ROOT}/items.json"

with open(PATH_CFG_FILE, "r", encoding="utf8") as f:
    config = yaml.safe_load(f)

TG_BOT_TOKEN = config["TG_BOT_TOKEN"]
USDT_API_TOKEN = config["USDT_API_TOKEN"]
USDT_API_URL = config["USDT_API_URL"]
NOTIFY_URL = config["NOTIFY_URL"]
REDIRECT_URL = config["REDIRECT_URL"]
WALLET_TOKEN = config["WALLET_TOKEN"]
WALLET_PHOTO = config["WALLET_PHOTO"]
EXPIRE_TIME_SECOND = config["EXPIRE_TIME_SECOND"]
REDIS_HOST = config["REDIS_HOST"]
REDIS_PORT = config["REDIS_PORT"]
REDIS_PASSWORD = config["REDIS_PASSWORD"]
ADMIN_TG_ACCOUNT = config["ADMIN_TG_ACCOUNT"]
ADMIN_TG_ID = config["ADMIN_TG_ID"]

with open(PATH_ITEMS_FILE, "r", encoding="utf8") as f:
    ITEMS = json.load(f)["items"]
    ITEMS = list(filter(lambda x: x["status"] == 1, ITEMS))