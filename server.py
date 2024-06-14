# pm2 start server.py --name pay-server --interpreter ~/Codes/tg-pay-bot/.venv/bin/python3
# pm2 start server.py --name pay-server --interpreter python3
import uvicorn
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
import redis
import sqlite3
import json
import cfg
import time
import threading


class PayResult(BaseModel):
    trade_id: str
    order_id: str
    amount: float
    actual_amount: float
    token: str
    block_transaction_id: str
    signature: str
    status: int  # 1: waiting 2: success 3: outdated


APP = FastAPI()
try:
    REDIS_CLI = redis.Redis(
        host=cfg.REDIS_HOST, port=cfg.REDIS_PORT, password=cfg.REDIS_PASSWORD
    )
except Exception:
    print("Redis is not working.")
BOT = telebot.TeleBot(cfg.TG_BOT_TOKEN, parse_mode="html")


def jbot_add_token(user_id):
    conn = sqlite3.connect(f"{cfg.PATH_USER_ROOT}/.tg_jav_bot_plus/tg_jav_bot_plus.db")
    conn.cursor().execute("UPDATE t_user SET balance=balance+? WHERE user_id=?", (160, user_id))
    conn.commit()

    BOT.send_message(chat_id=user_id, text="付款成功！商品已发放，请查收～")
    BOT.send_message(
        chat_id=cfg.ADMIN_TG_ID,
        text=f"[tg-pay-bot#jbot_add_token] 用户{user_id}付款成功",
    )


def jbot_set_vip(user_id):
    conn = sqlite3.connect(f"{cfg.PATH_USER_ROOT}/.tg_jav_bot_plus/tg_jav_bot_plus.db")
    conn.cursor().execute("UPDATE t_user SET is_vip=? WHERE user_id=?", (1, user_id))
    conn.commit()

    BOT.send_message(chat_id=user_id, text="付款成功！商品已发放，请查收～")
    BOT.send_message(
        chat_id=cfg.ADMIN_TG_ID, text=f"[tg-pay-bot#jbot_set_vip] 用户{user_id}付款成功"
    )


def jbot_set_svip(user_id):
    conn = sqlite3.connect(f"{cfg.PATH_USER_ROOT}/.tg_jav_bot_plus/tg_jav_bot_plus.db")
    conn.cursor().execute("UPDATE t_user SET is_svip=? WHERE user_id=?", (1, user_id))
    conn.commit()

    BOT.send_message(chat_id=user_id, text="付款成功！商品已发放，请查收～")
    BOT.send_message(
        chat_id=cfg.ADMIN_TG_ID,
        text=f"[tg-pay-bot#jbot_set_svip] 用户{user_id}付款成功",
    )


def code_service(user_id):
    ts = time.time()
    BOT.send_message(chat_id=cfg.ADMIN_TG_ID, text=f"代码服务: {ts}")
    BOT.send_message(
        chat_id=user_id,
        text=f"付款成功！您的服务码为：{ts}，将服务码发给管理员即可，同时可列出您的需求，协商完成后将尽快为您启动开发～",
        reply_markup=InlineKeyboardMarkup().row(
            InlineKeyboardButton("联系管理员", url=cfg.ADMIN_TG_ACCOUNT)
        ),
    )


@APP.post("/notify")
def notify(res: PayResult):
    order_id = res.order_id
    user_id_item_id = order_id[order_id.rfind("-") + 1:]
    s = user_id_item_id.find("#")
    user_id = user_id_item_id[:s]
    item_id = int(user_id_item_id[s + 1:])
    item = cfg.ITEMS[item_id]
    if res.status == 2:
        threading.Thread(target=globals()[item["action"]], args=(user_id,)).start()
        return Response("ok", status_code=200)
    elif res.status == 3:
        BOT.send_message(user_id, "订单已过期")
        return Response("ok", status_code=200)


@APP.get("/redirect")
def redirect():
    return Response("ok", status_code=200)


if __name__ == "__main__":
    uvicorn.run("server:APP", host="0.0.0.0", port=8081, reload=True)
