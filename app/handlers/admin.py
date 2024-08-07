from datetime import datetime
from asyncio import sleep

from aiogram import types
from aiogram.types import ChatType
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound
from aiogram.dispatcher.filters.builtin import Text
from loguru import logger

from loader import dp, qiwis
from models import User
from data import payload
from data.states import AdminPanel
from data.config import ADMINS_ID, PAY_ROWS
from keyboards import *


""" admin panel """


def check_admin(chat_id: int):
    """
    Проверка являеться ли юзер админом
    """
    if chat_id in ADMINS_ID:
        return True
    else:
        logger.info(f"#{chat_id} - try admin panel")


@dp.message_handler(
    Text(startswith="админ", ignore_case=True), state="*", chat_type=ChatType.PRIVATE
)
async def admin_panel(message: types.Message, state: FSMContext):
    """
    Перевод на различные стейты из админ панели
    """
    if check_admin(message.chat.id):
        await message.answer(
            "Админка, выберете действие...", reply_markup=admin_keyboard
        )
        # Set state
        await AdminPanel.main.set()


@dp.message_handler(
    Text(startswith="qiwi", ignore_case=True),
    state=AdminPanel.main,
    chat_type=ChatType.PRIVATE,
)
async def qiwi_main(message: types.Message):
    if check_admin(message.chat.id):
        main_balance = 0
        balances = ""
        for qiwi in qiwis:
            api = qiwis[qiwi]
            balance = await api.balance
            main_balance += balance["amount"]
            balances += f"<code>{qiwi}</code>: <b>{balance['amount']} RUB</b> ({balance['currency']})\n"
        await message.answer(
            f"{balances}Общая сумма: <b>{main_balance} RUB</b>\nВыберите кошелек.",
            reply_markup=qiwi_keyboard,
        )


@dp.message_handler(
    Text(startswith="изменить", ignore_case=True),
    state=AdminPanel.main,
    chat_type=ChatType.PRIVATE,
)
async def change_balance_id(message: types.Message):
    if check_admin(message.chat.id):
        await message.answer("Введи тилеграм айди юзира")
        await AdminPanel.change_balance_id.set()


@dp.message_handler(
    lambda msg: not msg.text.isdigit(),
    state=AdminPanel.change_balance_id,
    chat_type=ChatType.PRIVATE,
)
async def invalid_change_balance_amount(message: types.Message):
    await message.answer("Неправильна ввел еще раз введи или иди нахуй")


@dp.message_handler(
    state=AdminPanel.change_balance_id,
    chat_type=ChatType.PRIVATE,
)
async def change_balance_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["cid"] = int(message.text)

    await message.answer("Ввиди сумму баланса чторбы изменить епта")
    await AdminPanel.change_balance_amount.set()


@dp.message_handler(
    lambda msg: not msg.text.isdigit(),
    state=AdminPanel.change_balance_amount,
    chat_type=ChatType.PRIVATE,
)
async def invalid_change_balance(message: types.Message):
    await message.answer("непрпавильный баланс еще введи епта")


@dp.message_handler(
    state=AdminPanel.change_balance_amount,
    chat_type=ChatType.PRIVATE,
)
async def change_balance_done(message: types.Message, state: FSMContext):
    amount = int(message.text)
    async with state.proxy() as data:
        chat_id = data["cid"]

    try:
        user = User.get(cid=chat_id)
    except User.DoesNotExist:
        await message.answer("Юзира с таким айди нету епта")
        return

    user.balance = amount
    user.save()

    await message.answer("Изменил баланс!!!")


@dp.callback_query_handler(lambda cb: cb.data.split("_")[0] == "qiwis", state="*")
async def qiwi_lasttr(query: types.CallbackQuery):
    if check_admin(query.message.chat.id):
        balance = await qiwis[query.data.split("_")[1]].balance
        payments = await qiwis[query.data.split("_")[1]].last_recharges(PAY_ROWS)
        last_payments = f"<b>{query.data.split('_')[1]}</b>\n<b>{balance['amount']} RUB</b> ({balance['currency']}) \
			\nПоследние пополнения:"

        for payment in payments:
            dateptime = datetime.strptime(payment["date"], "%Y-%m-%dT%H:%M:%S+03:00")
            date = (
                f"{dateptime.hour}:{dateptime.minute} {dateptime.day}.{dateptime.month}"
            )

            currency = (
                " RUB"
                if payment["sum"]["currency"] == 643
                else f"({payment['sum']['currency']})"
            )
            last_payments += f"\n<b>{payment['sum']['amount']}{currency}</b> {payment['comment']}: {payment['account']},\
				<i>{date}</i>"

        await query.message.answer(last_payments)


@dp.message_handler(
    Text(startswith="посл", ignore_case=True),
    state=AdminPanel.main,
    chat_type=ChatType.PRIVATE,
)
async def last_users(message: types.Message):
    if check_admin(message.chat.id):
        users = User.select().order_by(User.id.desc())
        text = f"Последние {PAY_ROWS} юзеров"

        for i in range(PAY_ROWS):
            try:
                user = users[i]
                text += f"\n@{user.username} {user.fullname}: <b>{user.balance:.2f} RUB</b>\
					\nInfo: [<code>{user.cid}</code>], {user.id}"
            except IndexError:
                break

        await message.answer(text, reply_markup=admin_keyboard)


@dp.message_handler(
    Text(startswith="оповещ", ignore_case=True),
    state=AdminPanel.main,
    chat_type=ChatType.PRIVATE,
)
async def notify_all(message: types.Message, state: FSMContext):
    if check_admin(message.chat.id):
        await message.answer("Введите текст для оповещения")
        await AdminPanel.notify.set()


@dp.message_handler(state=AdminPanel.notify, chat_type=ChatType.PRIVATE)
async def notify_sure(message: types.Message, state: FSMContext):
    if check_admin(message.chat.id):
        await message.answer(f"{message.text}", reply_markup=notify_keyboard)
        async with state.proxy() as data:
            data["msg"] = message.text
        await AdminPanel.main.set()


@dp.callback_query_handler(text="sure", state="*")
async def admin_down(query: types.CallbackQuery, state: FSMContext):
    if check_admin(query.message.chat.id):
        async with state.proxy() as data:
            data["msg"]
            await query.message.edit_text(
                "Рассылка пошла\nСообщений отправлено: <b>0</b>"
            )
            await AdminPanel.main.set()

            msges = 0
            for user in User.select().order_by(User.id.desc()):
                if user.alerts:
                    try:
                        await dp.bot.send_message(user.cid, data["msg"])
                        logger.debug(f"send message to {user.cid}")
                        msges += 1
                        await query.message.edit_text(
                            f"Рассылка пошла\nСообщений отправлено: <b>{msges}</b>"
                        )
                        await sleep(0.15)
                    except Exception:
                        logger.debug("Чат с пользователем не найден")


@dp.callback_query_handler(lambda cb: cb.data.split("_")[0] == "outreq", state="*")
async def send_money(query: types.CallbackQuery, state: FSMContext):
    if check_admin(query.message.chat.id):
        await query.answer(f"Перевожу {query.data.split('_')[1]} RUB")
        for qiwi in qiwis:
            api = qiwis[qiwi]
            balance = await api.balance
            if balance["amount"] * 1.2 > int(query.data.split("_")[1]):
                await api.pay(
                    query.data.split("_")[2],
                    int(query.data.split("_")[1]),
                    comment="B7 Invest",
                )
                await query.message.edit_text(
                    f"Перевел! {query.data.split('_')[2]}, {int(query.data.split('_')[1])}"
                )
                await dp.bot.send_message(
                    query.data.split("_")[3], payload.out_done_otz
                )
                return
            await query.message.answer("Баланса не хватает")
    else:
        await query.answer(
            f"Чат не является админом {query.message.chat.id}", show_alert=True
        )
