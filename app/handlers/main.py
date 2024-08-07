from datetime import datetime

from aiogram import types
from aiogram.types import ChatType
from aiogram.dispatcher import FSMContext
from loguru import logger

from data import payload
from data.states import Calculator
from data.config import SHARE, CHANNEL_ID
from models import User, UserHistory
from keyboards import *
from loader import dp


@dp.message_handler(regexp="назад", state="*", chat_type=ChatType.PRIVATE)
@dp.message_handler(commands="start", state="*", chat_type=ChatType.PRIVATE)
async def welcome(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        logger.info(f"Cancelling state {current_state}")
        await state.finish()

    ref_id = 0
    try:
        ref_id = message.text.split()[1]
    except IndexError:
        logger.debug(f"{message.chat.first_name} #{message.chat.id} with out ref.")
    try:
        user = User.get(cid=message.chat.id)
        await message.answer(payload.welcome_text, reply_markup=main_keyboard)
    except User.DoesNotExist:
        username = message.chat.username
        if username is None:
            username = "Нету"
        User.create(
            cid=message.chat.id,
            refer=ref_id,
            username=username,
            fullname=message.chat.full_name,
            registered=datetime.now(),
        )
        await message.answer(payload.new_text, reply_markup=new_keyboard)


@dp.callback_query_handler(text="cjoin")
async def main_menu(query: types.CallbackQuery, state: FSMContext):
    chat_member = await dp.bot.get_chat_member(
        chat_id=CHANNEL_ID, user_id=query.message.chat.id
    )
    if chat_member.status == "left":
        await query.answer("Вы не подписаны!", show_alert=True)
    else:
        await query.message.delete()
        await welcome(query.message, state)


@dp.message_handler(regexp="инвест", state="*", chat_type=ChatType.PRIVATE)
async def invest(message: types.Message):
    text = payload.invest_text(message.chat.id)
    if text:
        await message.answer(text, reply_markup=invest_keyboard)
    else:
        await message.answer("Какая-то ошибка, /start")


@dp.message_handler(regexp="парт", state="*", chat_type=ChatType.PRIVATE)
async def partners(message: types.Message):
    await message.answer(
        await payload.partners_text(message.chat.id), reply_markup=refer_keyboard
    )


@dp.message_handler(regexp="кальк", state="*", chat_type=ChatType.PRIVATE)
async def calculator(message: types.Message):
    await message.answer(payload.calc_text, reply_markup=main_keyboard)
    await Calculator.main.set()


@dp.message_handler(regexp="настр", state="*", chat_type=ChatType.PRIVATE)
async def settings(message: types.Message):
    await message.answer(payload.settings_text(), reply_markup=settings_keyboard)


@dp.callback_query_handler(text="alerts", state="*")
async def alerts(query: types.CallbackQuery):
    try:
        user = User.get(cid=query.message.chat.id)
        user.alerts = not user.alerts
        user.save()
        status = "Вкл." if user.alerts else "Выкл."
        await query.answer(f"Уведомления: {status}")
    except User.DoesNotExist:
        pass


@dp.callback_query_handler(text="operations", state="*")
async def operations(query: types.CallbackQuery):
    try:
        history = UserHistory.select().where(UserHistory.cid == query.message.chat.id)
        if not history:
            text = "У вас нету операций!"
        else:
            text = "<i>Ваши последнии операции</i>:\n"
            for hist in history:
                if hist.editor == 0:
                    status = "Пополнение"
                elif hist.editor == 1:
                    status = "Вывод"
                elif hist.editor == 2:
                    status = "Ре-инвестирование"
                elif hist.editor == 3:
                    status = "Сбор"

                text += f"{status}: <b>{hist.amount:.2f} RUB, {hist.created:%d %b %H:%M}</b>\n"
        await query.message.answer(text)
    except User.DoesNotExist:
        pass


@dp.message_handler(regexp="обуч", state="*", chat_type=ChatType.PRIVATE)
async def manual(message: types.Message):
    await message.answer(payload.manual_text, reply_markup=manual_keyboard)


@dp.message_handler(
    lambda mes: not mes.text.isdigit(),
    state=Calculator.main,
    chat_type=ChatType.PRIVATE,
)
async def calculator_inv(message: types.Message):
    await message.answer(payload.calc_inv, reply_markup=main_keyboard)


@dp.message_handler(state=Calculator.main, chat_type=ChatType.PRIVATE)
async def calculator_done(message: types.Message, state: FSMContext):
    amount = int(message.text)
    if amount > 1000000:
        await message.answer(payload.calc_tomuch, reply_markup=main_keyboard)
    elif amount < 100:
        await message.answer(payload.calc_tosmall, reply_markup=main_keyboard)
    else:
        await message.answer(payload.calc_done(amount), reply_markup=main_keyboard)
        await state.finish()


@dp.callback_query_handler(text="collect", state="*")
async def collect(query: types.CallbackQuery):
    try:
        user = User.get(cid=query.message.chat.id)
        timesince = datetime.now() - user.collected
        storage = round(
            user.storaged
            + timesince.total_seconds() / 86400 * user.invested * SHARE / 100,
            2,
        )
        if storage < 1:
            await query.answer(payload.collect_tosmall, show_alert=True)
        else:
            await query.answer(payload.collect_done(storage), show_alert=True)
            user.balance += storage
            user.storaged = 0
            user.collected = datetime.now()
            UserHistory.create(cid=query.message.chat.id, amount=storage, editor=3)
            user.save()
            text = payload.invest_text(message.chat.id)
            if text:
                await query.message.edit_text(text, reply_markup=invest_keyboard)
            else:
                await query.message.edit_text("Какая-то ошибка, /start")
    except User.DoesNotExist:
        pass


@dp.callback_query_handler(text="invest", state="*")
async def collect(query: types.CallbackQuery):
    try:
        user = User.get(cid=query.message.chat.id)
        if user.balance < 100:
            await query.answer(payload.invest_tosmall, show_alert=True)
        else:
            timesince = datetime.now() - user.collected
            storage = round(
                user.storaged
                + timesince.total_seconds() / 86400 * user.invested * SHARE / 100,
                2,
            )
            await query.answer(payload.invest_done(user.balance), show_alert=True)
            UserHistory.create(cid=query.message.chat.id, amount=user.balance, editor=2)
            user.invested += user.balance
            user.balance = 0
            user.storaged += storage
            user.collected = datetime.now()
            user.save()
    except User.DoesNotExist:
        pass
