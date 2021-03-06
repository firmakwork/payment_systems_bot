from telebot import types

pay_subscription_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="оформить подписку", callback_data="pay_subscription"))

choice_type_payment = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Юкасса", callback_data="yookassa"),
    types.InlineKeyboardButton(text="Интеркасса", callback_data="interkassa")

)
choice_period_subscription = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="3 дня", callback_data="3"),
    types.InlineKeyboardButton(text="10 дней", callback_data="10"),
    types.InlineKeyboardButton(text="30 дней", callback_data="30"),
    types.InlineKeyboardButton(text="назад", callback_data="pay_subscription"))

back_to_choice_period_subscription = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_to_choice_period_subscription")
)
