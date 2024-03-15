import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import json
import hashlib
import requests
import time
import redis
import cfg

if cfg.REDIS_PASSWORD:
    REDIS_CLI = redis.Redis(
        host=cfg.REDIS_HOST, port=cfg.REDIS_PORT, password=cfg.REDIS_PASSWORD
    )
else:
    REDIS_CLI = redis.Redis(host=cfg.REDIS_HOST, port=cfg.REDIS_PORT)
BOT = telebot.TeleBot(cfg.TG_BOT_TOKEN, parse_mode="html")


@BOT.message_handler(content_types=["text"])
def handle_message(message):
    user_id = message.from_user.id
    cmd = message.text

    print(f"收到消息: {cmd}")

    if cmd == "/items" or cmd == "/start" or cmd == "/start 1":
        mk = InlineKeyboardMarkup()
        for i, item in enumerate(cfg.ITEMS):
            mk.row(InlineKeyboardButton(item["name"], callback_data=f"item:{i}"))
        BOT.send_message(
            chat_id=user_id,
            text="""在售商品列表, 点击商品即可查看详情或下单。下单后将返回付款码，请根据提示在指定时间内完成付款，否则订单作废。

代码类服务完成付款后将自动返回服务码，将服务码发给管理员即可，同时可列出您的需求，协商完成后将尽快为您启动开发～                                         
""",
            reply_markup=mk,
        )
    else:
        BOT.reply_to(
            message,
            f"""/items 查看在售商品列表
/help 查看帮助""",
        )


@BOT.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.from_user.id)
    data = call.data

    print(f"处理回调: {data}")

    s = data.rfind(":")
    content = data[:s]
    key_type = data[s + 1 :]
    BOT.send_chat_action(chat_id=user_id, action="typing")
    if content == "item":
        item = cfg.ITEMS[int(key_type)]
        item_detail = f"""🚀<b>{item['name']}</b>

🖥{item['desc']}

💰{item['price']} 元(付款时根据实时汇率转为 USDT)
"""
        BOT.send_message(
            chat_id=user_id,
            text=item_detail,
            reply_markup=InlineKeyboardMarkup().row(
                InlineKeyboardButton("下单", callback_data=f"buy:{key_type}"),
                InlineKeyboardButton("联系管理员", url=cfg.ADMIN_TG_ACCOUNT),
            ),
        )
    elif content == "buy":
        item = cfg.ITEMS[int(key_type)]
        amount = int(item["price"])
        order_id = f"tg-pay-bot-{user_id}#{key_type}"
        if REDIS_CLI.get(order_id):
            BOT.send_message(chat_id=user_id, text="该商品已经有进行中的订单!")
            return
        REDIS_CLI.set(name=order_id, value=1, ex=cfg.EXPIRE_TIME_SECOND)
        signature = hashlib.md5(
            f"amount={amount}&notify_url={cfg.NOTIFY_URL}&order_id={order_id}&redirect_url={cfg.REDIRECT_URL}{cfg.USDT_API_TOKEN}".encode()
        ).hexdigest()
        response = requests.post(
            cfg.USDT_API_URL,
            json={
                "order_id": order_id,
                "amount": amount,
                "notify_url": cfg.NOTIFY_URL,
                "redirect_url": cfg.REDIRECT_URL,
                "signature": signature,
            },
        )
        if response.status_code != 200:
            BOT.send_message(chat_id=user_id, text="创建订单失败，请重试或联系管理员～")
            return
        data = response.json()["data"]
        usdt_amount = data["actual_amount"]
        # payment_url = data["payment_url"]
        BOT.send_photo(
            chat_id=user_id,
            photo=cfg.WALLET_PHOTO,
            caption=f"""📺订单明细:
            
💰需要支付: {usdt_amount} USDT

🤖网络: USDT-TRC20

🎯钱包地址: {cfg.WALLET_TOKEN}

🚦扫码如上二维码进行支付即可，请确保在 {int(cfg.EXPIRE_TIME_SECOND / 60)} 分钟内完成支付, 支付金额必须和显示金额保持一致。""",
        )


BOT_CMDS = {"items": "查看商品列表", "help": "帮助"}
BOT.set_my_commands([BotCommand(cmd, BOT_CMDS[cmd]) for cmd in BOT_CMDS])

if __name__ == "__main__":
    BOT.infinity_polling()
