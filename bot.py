# pm2 start bot.py --name pay-bot --interpreter ~/Codes/tg-pay-bot/.venv/bin/python3
# pm2 start bot.py --name pay-bot --interpreter python3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import hashlib
import requests
import redis
import cfg

LOG = cfg.Logger(path_log_file=cfg.PATH_LOG_FILE).logger
if cfg.REDIS_PASSWORD:
    REDIS_CLI = redis.Redis(
        host=cfg.REDIS_HOST, port=cfg.REDIS_PORT, password=cfg.REDIS_PASSWORD
    )
else:
    REDIS_CLI = redis.Redis(host=cfg.REDIS_HOST, port=cfg.REDIS_PORT)
BOT = telebot.TeleBot(cfg.TG_BOT_TOKEN, parse_mode="html")
OKX_UID = "440186776666407525"


@BOT.message_handler(content_types=["text"])
def handle_message(message):
    user_id = message.from_user.id
    cmd = message.text

    LOG.info(f"[tg-pay-bot] 收到消息: {cmd}")

    if cmd == "/items" or cmd == "/start" or cmd == "/start 1":
        mk = InlineKeyboardMarkup()
        for i, item in enumerate(cfg.ITEMS):
            mk.row(InlineKeyboardButton(item["name"], callback_data=f"item:{i}"))
        BOT.send_message(
            chat_id=user_id,
            text="""在售商品列表, 点击商品即可查看详情或下单。                                      
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

    LOG.info(f"[tg-pay-bot] 处理回调: {data}")

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
            reply_markup=InlineKeyboardMarkup()
            .row(
                InlineKeyboardButton("下单", callback_data=f"buy:{key_type}"),
                InlineKeyboardButton("联系管理员", url=cfg.URL_ADMIN_TG_ACCOUNT),
            )
            .row(InlineKeyboardButton("反馈交流群", url=cfg.URL_FEEDBACK_GROUP)),
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
        trade_id = data["trade_id"]
        usdt_amount = data["actual_amount"]
        # payment_url = data["payment_url"]
        BOT.send_photo(
            chat_id=user_id,
            photo=cfg.WALLET_PHOTO,
            caption=f"""📺请扫码进行支付或手动输入网络和钱包地址完成付款。
            
💰需要支付: <code>{usdt_amount}</code> USDT

🤖网络: <code>USDT-TRC20</code>

🎯钱包地址: <code>{cfg.WALLET_TOKEN}</code>

⚡️注意支付金额必须和显示金额保持一致，请确保在 {int(cfg.EXPIRE_TIME_SECOND / 60)} 分钟内完成支付，超时则订单失效。

❤️如果您已经付款成功但未能收到商品，请联系管理员 {cfg.NAME_ADMIN} 或在群组 {cfg.NAME_FEEDBACK_GROUP} 反馈，注意发送付款成功的截图进行反馈哟！
""",
            # PS: 以上付款方式为链上提币，如果你使用欧易则可使用内部转账付款，付款时选择转账方式为UID，UID填写 <code>{OKX_UID}</code> 即可。内部转账成功后需将截图发给管理员，而链上提币不需要，机器人将自动处理。
            reply_markup=InlineKeyboardMarkup().row(
                InlineKeyboardButton("联系管理员", url=cfg.URL_ADMIN_TG_ACCOUNT),
                InlineKeyboardButton("反馈交流群", url="https://t.me/jav_bot_group"),
            ),
            # .row(InlineKeyboardButton("查看订单状态", url=f"https://pay.akynazh.site/pay/checkout-counter/{trade_id}"),)
        )


BOT_CMDS = {"items": "查看商品列表", "help": "帮助"}
BOT.set_my_commands([BotCommand(cmd, BOT_CMDS[cmd]) for cmd in BOT_CMDS])

if __name__ == "__main__":
    BOT.infinity_polling()
