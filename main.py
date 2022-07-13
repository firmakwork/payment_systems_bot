import telebot
from flask import Flask, request
import bs4
from config import *
from keyboard import *
from classes import *

bot = telebot.TeleBot(token=api_key_bot)
users = Users()

app = Flask(__name__)


@app.route(f'/{api_key_bot}', methods=["POST", "GET"])
def handle():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "ok", 200


@app.route('/pay', methods=["POST", "GET"])
def index():
    user_id = int(request.args.get('user_id'))
    subscription_period = int(request.args.get('subscription_period'))
    user = users.get_elem(user_id)
    if subscription_period == user.subscription:
        return users.create_pay(id=user_id, price=user.price)
    else:
        bot.edit_message_text(chat_id=user_id,
                              text="Произошла ошибка\nПопробуйте ещё раз",
                              message_id=user.message_id)
        return 404


@bot.message_handler(commands=['start'])
def start(message):
    global users
    user_id = int(message.from_user.id)
    if user_id in users:
        user = users.get_elem(user_id)
        bot.edit_message_text(chat_id=user_id,
                              text=f"Привет, {user.fio}",
                              reply_markup=pay_subscription_keyboard,
                              message_id=user.message_id)
    else:
        users += user_id
        user = users.get_elem(user_id)
        user.username = message.from_user.username
        r = bot.send_message(chat_id=user_id,
                             text=f"Привет, {user.username}\n Введи свое ФИО")
        user.message_id = r.id
        user.flag = 1


@bot.message_handler(content_types="text", func=lambda message: message.from_user.id in users
                                                                and users.get_elem(int(message.from_user.id)).flag == 1)
def fio(message):
    global users
    user_id = int(message.from_user.id)
    user = users.get_elem(user_id)
    user.fio = message.text
    bot.delete_message(chat_id=user_id,
                       message_id=message.id)

    bot.edit_message_text(chat_id=user_id,
                          text=f"Привет, {user.fio}",
                          reply_markup=pay_subscription_keyboard,
                          message_id=user.message_id)
    user.flag = 0


@bot.callback_query_handler(func=lambda call: call.data == "pay_subscription")
def pay_subscription(call):
    global users
    user_id = int(call.from_user.id)
    user = users.get_elem(user_id)
    bot.edit_message_text(chat_id=user_id,
                          text="Выбери платежную систему",
                          reply_markup=choice_type_payment,
                          message_id=user.message_id)


@bot.callback_query_handler(func=lambda call: call.data in ["yookassa", "interkassa"])
def pay_subscription(call):
    global users
    user_id = int(call.from_user.id)
    user = users.get_elem(user_id)
    user.set_type_payment(call.data)

    if user.type_payment == "yookassa":
        if user.invoice_id > 0:
            bot.delete_message(chat_id=user_id,
                               message_id=user.invoice_id)
            r = bot.send_message(chat_id=user_id,
                                 text="Выбери срок подписки",
                                 reply_markup=choice_period_subscription)
            user.invoice_id = -1
            user.message_id = r.id
        else:
            bot.edit_message_text(chat_id=user_id,
                                  text="Выбери срок подписки",
                                  reply_markup=choice_period_subscription,
                                  message_id=user.message_id)

    elif user.type_payment == "interkassa":
        bot.edit_message_text(chat_id=user_id,
                              text="Выбери срок подписки",
                              reply_markup=choice_period_subscription,
                              message_id=user.message_id)

@bot.callback_query_handler(func=lambda call: call.data in ["3", "10", "30"])
def pay_subscription(call):
    global users
    user_id = int(call.from_user.id)
    user = users.get_elem(user_id)

    if "3" == call.data:
        user.set_type_subscription(3)
        user.set_price(400 * 10 ** 2)

    elif "10" == call.data:
        user.set_type_subscription(10)
        user.set_price(800 * 10 ** 2)

    elif "30" == call.data:
        user.set_type_subscription(30)
        user.set_price(1800 * 10 ** 2)

    if user.type_payment == "interkassa":
        keyboard = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton(text="оплатить",
                                       url=f"https://6225-45-137-112-86.ngrok.io/pay?user_id={user_id}&"
                                           f"subscription_period={user.subscription}"),
            types.InlineKeyboardButton(text="назад", callback_data=user.type_payment))
        bot.edit_message_text(chat_id=user_id,
                              text="Нажав на кнопку Вы попадете на страницу, которая ведет на интеркассу",
                              reply_markup=keyboard,
                              message_id=user.message_id)

    elif user.type_payment == "yookassa":
        price = types.LabeledPrice(label='подписка', amount=user.price)
        keyboard = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton("оплатить", pay=True),
            types.InlineKeyboardButton(text="назад", callback_data=user.type_payment))
        bot.delete_message(chat_id=user_id,
                           message_id=user.message_id)
        r = bot.send_invoice(chat_id=user_id,
                             title=f"подписка на {user.subscription} дня/дней",
                             description=f"test",
                             provider_token=provider_token,
                             prices=[price],
                             invoice_payload=str(user_id),
                             currency="RUB",
                             reply_markup=keyboard)
        user.invoice_id = r.id


if __name__ == "__main__":
    WEBHOOK_PORT = 80
    WEBHOOK_LISTEN = '0.0.0.0'
    bot.delete_webhook()
    bot.set_webhook(url=url+f"/{api_key_bot}")
    app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, debug=False)
    #bot.infinity_polling()
