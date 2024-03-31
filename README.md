## tg-pay-bot

A telegram USDT-TRC20 collection robot.

## usage

```sh
# python >= 3.10
pip install -r requirements.txt

# edit ~/.tg_pay_bot/config.yml >> bot config >> template:
TG_BOT_TOKEN: YOUR_TG_BOT_TOKEN
USDT_API_TOKEN: YOUR_USDT_API_TOKEN
USDT_API_URL: xxx/api/v1/order/create-transaction
NOTIFY_URL: xxx/server/notify
REDIRECT_URL: xxx/server/redirect
WALLET_TOKEN: YOUR_USDT_WALLET_TOKEN
WALLET_PHOTO: YOUR_USDT_WALLET_IMAGE
EXPIRE_TIME_SECOND: 600
ADMIN_TG_ACCOUNT: TG_ADMIN_TG_ACCOUNT
ADMIN_TG_ID: TG_ADMIN_TG_ID
# optional:
REDIS_HOST: localhost
REDIS_PORT: 6379
REDIS_PASSWORD: YOUR_REDIS_PASSWORD

# edit ~/.tg_pay_bot/items.json >> stuffs to sell >> template:
{
    "items": [
        {
            "name": "xx vip",
            "desc": "xxx",
            "price": "35",
            "action": "set_vip"
        },
    ]
}

# edit your action in server.py:
def set_vip(user_id):
    # ...
    BOT.send_message(chat_id=user_id, text="success")

# run
python3 bot.py
python3 server.py
```
