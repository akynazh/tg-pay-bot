import yaml
import json
import os
import logging
from logging.handlers import RotatingFileHandler

PATH_USER_ROOT = os.path.expanduser("~")
PATH_PAY_BOT_ROOT = f"{PATH_USER_ROOT}/.tg_pay_bot"
PATH_CFG_FILE = f"{PATH_PAY_BOT_ROOT}/config.yml"
PATH_ITEMS_FILE = f"{PATH_PAY_BOT_ROOT}/items.json"
PATH_LOG_FILE = f"{PATH_PAY_BOT_ROOT}/log.txt"

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
NAME_ADMIN = config["NAME_ADMIN"]
NAME_FEEDBACK_GROUP = config["NAME_FEEDBACK_GROUP"]
URL_FEEDBACK_GROUP = config["URL_FEEDBACK_GROUP"]
URL_ADMIN_TG_ACCOUNT = config["URL_ADMIN_TG_ACCOUNT"]
ADMIN_TG_ID = config["ADMIN_TG_ID"]

with open(PATH_ITEMS_FILE, "r", encoding="utf8") as f:
    ITEMS = json.load(f)["items"]
    ITEMS = list(filter(lambda x: x["status"] == 1, ITEMS))


class Logger:
    """日志记录器"""

    def __init__(self, path_log_file: str, log_level=logging.INFO):
        """初始化日志记录器

        :param str path_log_file: 日志记录文件
        :param int log_level: 记录级别, 默认 INFO 级别
        """
        self.logger = logging.getLogger()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        r_file_handler = RotatingFileHandler(
            path_log_file, maxBytes=1024 * 1024 * 16, backupCount=1
        )
        r_file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(r_file_handler)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(log_level)
