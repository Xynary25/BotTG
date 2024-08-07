from aiogram import types
from aiogram.types import ChatType
from loguru import logger

from loader import dp


@dp.message_handler(
    content_types=["new_chat_member", "left_chat_member"],
    state="*",
    chat_type=ChatType.SUPERGROUP,
)
async def delete_member_comand(message: types.Message):
    logger.debug(f"Deleting chat member msg: {message.from_user.id}")
    await message.delete()


# обязательно через | !!!
@dp.message_handler(
    regexp="скам|лох|обман|наеб|наёб|кидалово|кидок|scam|skam|ckам|skам",
    state="*",
    chat_type=ChatType.PRIVATE,
)
async def sskfiltrbot(message: types.Message):
    pass


@dp.message_handler(
    regexp="скам|лох|обман|наеб|наёб|кидалово|кидок|scam|skam|ckам|skам", state="*"
)
async def sskfiltr(message: types.Message):
    await message.delete()
    logger.info(f"Deleted bad msg from user [{message.from_user.id}]")
