from aiogram.utils.emoji import emojize
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import QIWI_ACCOUNTS

new_keyboard = InlineKeyboardMarkup(row_width=1)
chat_btn = InlineKeyboardButton(
    emojize(":heavy_plus_sign: Вступить в чат"),
    url="https://t.me/joinchat/mnshvBEeZdxmNmIy",
)
channel_btn = InlineKeyboardButton(
    emojize(":heavy_plus_sign: Подписаться на канал"),
    url="https://t.me/joinchat/mPYl0zeKpShiZTk6",
)
cjoin_btn = InlineKeyboardButton(
    emojize(":heavy_check_mark: Продолжить"), callback_data="cjoin"
)
new_keyboard.add(chat_btn, channel_btn, cjoin_btn)

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
invest_btn = KeyboardButton(emojize(":chart: Инвестиции"))
refers_btn = KeyboardButton(emojize(":necktie: Партнерам"))
balance_btn = KeyboardButton(emojize(":credit_card: Кошелек"))
calculator_btn = KeyboardButton(emojize(":fax: Калькулятор"))
settings_btn = KeyboardButton(emojize(":gear: Настройки"))
manual_btn = KeyboardButton(emojize(":green_book: Обучение"))
main_keyboard.add(
    invest_btn, refers_btn, balance_btn, calculator_btn, settings_btn, manual_btn
)

#
manual_keyboard = InlineKeyboardMarkup()
manual_btn = InlineKeyboardButton(
    emojize(":heavy_plus_sign: Открыть обучение"),
    url="https://telegra.ph/B7-Investicii-04-05",
)
manual_keyboard.add(manual_btn)

refer_keyboard = InlineKeyboardMarkup()
refer_btn = InlineKeyboardButton(
    emojize(":heavy_plus_sign: Как набрать парнетров?"),
    url="https://telegra.ph/B7-dlya-partnerov-04-05",
)
refer_keyboard.add(refer_btn)

settings_keyboard = InlineKeyboardMarkup(row_width=2)
alerts_btn = InlineKeyboardButton(emojize(":bell: Уведомления"), callback_data="alerts")
operations_btn = InlineKeyboardButton(
    emojize(":fax: Операции"), callback_data="operations"
)
info_btn = InlineKeyboardButton(
    emojize(":book: Информация"), url="https://telegra.ph/B7-Investicii-04-05"
)
licence_btc = InlineKeyboardButton(
    emojize(":lock: Соглашение"), url="https://telegra.ph/B7-soglashenie-04-06"
)
settings_keyboard.add(alerts_btn, operations_btn, info_btn, licence_btc)

invest_keyboard = InlineKeyboardMarkup()
invest_btn = InlineKeyboardButton(
    emojize(":heavy_plus_sign: Инвестировать"), callback_data="invest"
)
collect_btn = InlineKeyboardButton(
    emojize(":heavy_minus_sign: Собрать"), callback_data="collect"
)
invest_keyboard.add(invest_btn, collect_btn)

balance_keyboard = InlineKeyboardMarkup()
add_btn = InlineKeyboardButton(
    emojize(":heavy_plus_sign: Пополнить"), callback_data="add"
)
out_btn = InlineKeyboardButton(
    emojize(":heavy_minus_sign: Вывести"), callback_data="out"
)
balance_keyboard.add(add_btn, out_btn)

admin_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
paymode_button = KeyboardButton("Изменить баланс")
last_button = KeyboardButton("Последние юзеры")
notify_button = KeyboardButton("Оповещение")
qiwi_button = KeyboardButton("Qiwi")
cancel_button = KeyboardButton("Назад")
admin_keyboard.add(qiwi_button, notify_button)
admin_keyboard.add(last_button, paymode_button)
admin_keyboard.add(cancel_button)

qiwi_keyboard = InlineKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True, row_width=1
)
for acc in QIWI_ACCOUNTS:
    qiwi_keyboard.add(InlineKeyboardButton(acc, callback_data=f"qiwis_{acc}"))


def add_keyboard(comment: int, number):
    url = f"https://qiwi.com/payment/form/99?currency=RUB&amountInteger=10\
	&amountFraction=0&extra['account']={number}&extra['comment']={comment}"

    markup = InlineKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True, row_width=1
    )
    goto_button = InlineKeyboardButton(
        emojize("Перейти к оплате :arrow_heading_up:"), url=url
    )
    check_button = InlineKeyboardButton(
        emojize("Проверить оплату :recycle:"), callback_data=f"check_{comment}_{number}"
    )
    markup.add(goto_button, check_button)

    return markup


notify_keyboard = InlineKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
sure_button = InlineKeyboardButton(emojize(":warning: Lesss go?"), callback_data="sure")
notify_keyboard.add(sure_button)


def admins_out_keyboard(amount, req, cid):
    keyboard = InlineKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = InlineKeyboardButton(
        emojize(f":warning: Перевести {amount}"),
        callback_data=f"outreq_{amount}_{req}_{cid}",
    )
    keyboard.add(button)

    return keyboard
