import random
from datetime import datetime

from aiogram import types
from aiogram.types import ChatType
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound
from loguru import logger

from data import payload
from data.config import OUT_CHAT, ADMINS_CHAT, SHARE
from data.states import Out
from models import User, Payment, UserHistory
from keyboards import *
from loader import dp, qiwis


@dp.message_handler(regexp="кошел", state="*", chat_type=ChatType.PRIVATE)
async def balance(message: types.Message):
    await message.answer(payload.balance_text(message.chat.id),
                         reply_markup=balance_keyboard)


@dp.callback_query_handler(text="out", state="*")
async def out(query: types.CallbackQuery):
    try:
        user = User.get(cid=query.message.chat.id)
        if user.balance == 0:
            await query.answer("Выводить нечего!", show_alert=True)
            return
        await query.message.answer(payload.outsum_text)
        await Out.main.set()
    except User.DoesNotExist:
        pass


@dp.message_handler(lambda mes: not mes.text.isdigit(), state=Out.main, chat_type=ChatType.PRIVATE)
async def out_req_inv(message: types.Message):
    await message.answer(payload.out_req_inv)


@dp.message_handler(state=Out.main, chat_type=ChatType.PRIVATE)
async def out_req(message: types.Message, state: FSMContext):
    try:
        user = User.get(cid=message.chat.id)
        if int(message.text) < 15:
            await message.answer(payload.out_tosmall,
                                 reply_markup=main_keyboard)
            return
        elif user.balance < int(message.text):
            await message.answer(payload.out_tobig,
                                 reply_markup=main_keyboard)
            await state.finish()
            return
        async with state.proxy() as data:
            data["amount"] = message.text
        await message.answer(payload.out_req_text)
        await Out.req.set()
    except User.DoesNotExist:
        pass


@dp.message_handler(lambda mes: not mes.text.isdigit(),
                    state=Out.req, chat_type=ChatType.PRIVATE)
async def out_done_inv(message: types.Message):
    await message.answer(payload.out_done_inv)


@dp.message_handler(state=Out.req, chat_type=ChatType.PRIVATE)
async def out_done(message: types.Message, state: FSMContext):
    if len(message.text) < 5:
        await message.answer(payload.out_done_inv)
        return
    async with state.proxy() as data:
        amount = data["amount"]
    try:
        user = User.get(cid=message.chat.id)
        user.balance -= int(amount)
        if user.balance < 0:
            await message.answer("Ошибка!")
            await state.finish()
            return
        UserHistory.create(cid=message.chat.id, amount=amount,
                           editor=1, created=datetime.now())
        user.save()
        await message.answer(payload.out_done(amount, message.text),
                             reply_markup=main_keyboard)
        await dp.bot.send_message(ADMINS_CHAT, payload.admins_out(message.chat.id, amount, message.text),
                                  reply_markup=admins_out_keyboard(amount, message.text, message.chat.id))
    except User.DoesNotExist:
        pass
    finally:
        await state.finish()


@dp.callback_query_handler(text="add", state="*")
async def add_reqiz(query: types.CallbackQuery):
    try:
        user = User.get(cid=query.message.chat.id)
        number = random.choice(list(qiwis.keys()))
        pay = Payment.create(cid=query.message.chat.id)
        await query.message.answer(payload.add_text(pay.id, number),
                                   reply_markup=add_keyboard(pay.id, number))
    except User.DoesNotExist:
        logger.debug(f"#{message.chat.id} - does not exist")


@dp.callback_query_handler(lambda cb: cb.data.split("_")[0] == "check")
async def add_check(query: types.CallbackQuery):
    try:
        user = User.get(cid=query.message.chat.id)
        comment = query.data.split("_")[1]
        number = query.data.split("_")[2]
        try:
            user_payment = Payment.get(cid=query.message.chat.id, id=comment)

            payments = await qiwis[number].last_recharges(30)
            for payment in payments:
                if payment['sum']['currency'] == 643 and payment['comment'] == comment:
                    await query.message.delete()

                    amount = int(payment['sum']['amount'])
                    timesince = datetime.now() - user.collected
                    storage = round(
                        user.storaged + timesince.total_seconds() / 86400 * user.invested * SHARE / 100, 2)
                    user.storaged += storage
                    user.invested += amount
                    user.collected = datetime.now()
                    UserHistory.create(
                        cid=query.message.chat.id, amount=amount, editor=0, created=datetime.now())
                    user.save()
                    try:
                        ref = User.get(cid=user.refer)
                        ref.balance += amount * 0.1
                        ref.save()
                    except User.DoesNotExist:
                        pass
                    # shit
                    if OUT_CHAT:
                        fullname = query.message.chat.full_name
                        username = query.message.chat.username
                        await dp.bot.send_message(OUT_CHAT, emojize(f":call_me_hand: Пополнение счета\
							\nСумма: <b>{amount}</b> Всего: {user.invested:.2f}\
							\nЮзер: {fullname}, <b>{username}</b> [<code>{query.message.chat.id}</code>]"))
                        try:
                            await dp.bot.send_message(user.refer, f"Ваш реферал пополнил: <b>{amount} RUB</b>\
								\nВы получили: <b>{amount * 0.1:.2f} RUB</b>")
                        except ChatNotFound:
                            pass

                    await query.message.answer(payload.add_succesful(amount))
                    return  # skip unseccessss
        except Payment.DoesNotExist:
            logger.warning(
                f"for #{query.message.chat.id} - payment does not exist")
            await query.message.answer("Похоже вы уже оплатили этот счёт или он не существует.")
            return
        await query.message.answer(payload.add_unsuccesful)
    except User.DoesNotExist:
        logger.debug(f"#{query.message.chat.id} - does not exist")
