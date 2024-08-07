from datetime import datetime

from aiogram.utils.emoji import emojize
from aiogram.utils.deep_linking import get_start_link

from data.config import SHARE, START_DATE, SUPP
from models import User

new_text = emojize(
    "⁠<a href='https://telegra.ph/file/9a6aa7b1827337502c3dd.png'>:black_small_square:</a>\
	Для начала работы с ботом, пройдите небольшую проверку,\
	просто вступите в <a href='https://t.me/joinchat/i_LhZU7E7m8yMDcy'>чат</a>\
	и <a href='https://t.me/joinchat/mPYl0zeKpShiZTk6'>канал</a> ниже и нажмите кнопку продолжить.\
	\n\n:warning: Нажмите на <b>«Подписаться 1 и 2»</b>"
)

welcome_text = emojize(":snake: Главное меню.")


def invest_text(cid):
    try:
        user = User.get(cid=cid)
        timesince = datetime.now() - user.collected
        storage = (
            user.storaged
            + timesince.total_seconds() / 86400 * user.invested * SHARE / 100
        )
        if storage > 1 or storage == 0:
            h = 0
            m = 0
            s = 0
        else:
            need = (1 - storage) * 24 / (user.invested * SHARE / 100)
            h = int(need)
            m = int(need % 1 * 60)
            s = int(need % 1 * 60 % 1 * 60)

        timeswap = f"{h}:{m:02d}:{s:02d}"
        return emojize(
            f"<a href='https://telegra.ph/file/bbb7acd1d8538f5f6f0e4.png'>:black_small_square:</a>\
			Открывай <b>инвестиции</b> и получай <b>стабильную прибыль</b>\
			в данном разделе, после собирай <b>доход</b>:\
			\n\n:battery: Процент прибыли: <b>{SHARE}%</b>\
			\n:hourglass: Время доходности: <b>24 часа</b>\
			\n:date: Срок вклада: <b>Пожизненно</b>\
			\n\n:credit_card: Ваш вклад: <b>{user.invested:.2f} RUB</b>\
			\n:dollar: Накопление: <b>{storage:.2f} RUB</b>\
			\n\n:stopwatch: Время до сбора: <b>{timeswap}</b>"
        )
    except User.DoesNotExist:
        return None


async def partners_text(cid):
    try:
        refers = len(User.select().where(User.refer == cid))
        user = User.get(cid=cid)
        return emojize(
            f"<a href='https://telegra.ph/file/14d46d5dede94403b4388.png'>:black_small_square:</a>\
			Наша <b>партнерская программа</b> считается самой <b>эффективной</b>,\
			приглашай <b>друзей</b> и <b>получай деньги</b>\
			\n\n💰 Всего отчислений: <b>{user.ref_balance:.2f} RUB</b>\
			\n\n💳 Процент с инвестиций: <b>{SHARE * 2}%</b>\
			\n💵 Процент с выплаты: <b>{SHARE}%</b>\
			\n\n👥 Партнеров: <b>{refers} чел</b>\
			\n\n🔗 Ваша <b>реф-ссылка</b>: <b>{await get_start_link(cid)}</b>"
        )
    except User.DoesNotExist:
        return "Ошибка, /start"


def balance_text(cid):
    try:
        user = User.get(cid=cid)
        refers = len(User.select().where(User.refer == cid))
        return emojize(
            f"<a href='https://telegra.ph/file/c1a75613995a1e21e8759.png'>:gear:</a>\
			Ваш ID: [<code>{cid}</code>]\
			\n\n:moneybag: Ваш баланс: <b>{user.balance:.2f} RUB</b>\
			\n:busts_in_silhouette: Партнеров: <b>{refers} чел.</b>"
        )
    except User.DoesNotExist:
        return "Ошибка, /start"


calc_text = emojize(
    "⁠⁠:black_small_square: <b>Введите сумму, которую хотите рассчитать</b>:"
)

calc_inv = emojize(":warning: Введите корректную сумму!")

calc_tomuch = emojize(
    ":warning: Максимальная сумма инвестиции <b>1.000.000 RUB</b>, введите корректную сумму!"
)

calc_tosmall = emojize(
    ":warning: Минимальная сумма инвестиции <b>100 RUB</b>, введите корректную сумму!"
)


def calc_done(amount):
    return emojize(
        f"<a href='https://telegra.ph/file/da10b6e6431b8a7a05ecc.png'>:black_small_square:</a>\
		В данном разделе вы сумеете <b>рассчитать</b> вашу <b>прибыль</b>, от суммы <b>инвестиции</b>:\
		\n\n:dollar: Ваша инвестиция: <b>{amount} RUB</b> \
		\n\n:black_small_square: Прибыль в сутки: <b>{amount * SHARE / 100} RUB</b> \
		\n:black_small_square: Прибыль в месяц: <b>{SHARE / 100 * amount * 30.5:.2f} RUB</b> \
		\n:black_small_square: Прибыль в год: <b>{SHARE / 100 * amount * 364.75:.2f} RUB</b>"
    )


def settings_text():
    users_sum = User.select().order_by(User.id.desc()).get().id
    date = datetime.now()
    new_users = len(
        User.select().where(
            (User.registered.day == date.day)
            & (User.registered.month == date.month)
            & (User.registered.year == date.year)
        )
    )
    delta = datetime.now() - START_DATE

    return emojize(
        f"<a href='https://telegra.ph/file/84577295162c7008ceacb.png'>:black_small_square:</a>\
		Вы попали в раздел <b>настройки</b> бота, здесь вы можете <b>посмотреть статистику</b>,\
		а также узнать информацию или <b>отключить уведомления</b>.\
		\n\n:green_heart: Дней работаем: <b>{delta.days}</b>\
		\n\n:black_small_square: Всего инвесторов: <b>{users_sum}</b>\
		\n:black_small_square: Новых за 24 часа: <b>{new_users}</b>\
		\n:black_small_square: Онлайн: <b>{int(new_users / 3)}</b>"
    )


manual_text = emojize(
    "<a href='https://telegra.ph/file/e044c52f66b812c030361.png'>:mortar_board:</a>\
	<b>Попал</b> в бота, но не знаешь, что <b>делать?</b>\
	\nТогда <b>ознакомься</b> с нашим <b>минутным обучением</b>:"
)

add_text = lambda comm, num: emojize(
    f":inbox_tray: Оплата через <b>QIWI/банковской картой</b>\
	\n\n:credit_card: Номер кошелька бота: <b>{num}</b>\
	\n:speech_balloon: Комментарий к переводу: <b>{comm}</b>\
	\n\n<i>Переведите нужную сумму средств на номер кошелька указанный ниже,\
	оставив при этом индивидуальный </i><b>комментарий</b><i> перевода!</i>"
)

outsum_text = emojize(
    ":outbox_tray: <b>Введите сумму для совершения вывода средств</b>.\
	\n\n:dollar: Минимальная сумма: <b>15 RUB</b>"
)

out_req_inv = emojize(
    ":no_entry: <b>Вы</b> ввели <b>некорректную сумму</b> для вывода.\
	\n<i>Повторите Вашу команду!</i>"
)

out_tosmall = emojize(
    ":no_entry: <b>Вы</b> ввели слишком <b>маленькую сумму</b> для вывода.\
	\n<i>Повторите Вашу команду!</i>"
)

out_tobig = emojize(
    ":no_entry: На <b>Вашем</b> счету <b>не</b> достаточно средств для совершения <b>вывода</b>."
)

out_req_text = emojize(
    ":kiwi_fruit: Введите реквизиты <b>Qiwi кошелька</b> без '+'.\
	\n<i>Статус кошелька должен быть не менее основного!</i>"
)

out_done_inv = emojize(
    ":no_entry: <b>Вы</b> ввели <b>некорректные реквизиты</b> для вывода.\
	\n<i>Повторите Вашу команду!</i>"
)

out_done = lambda amount, req: emojize(
    f":white_check_mark: <b>Ваша заявка</b> на вывода <b>принята</b>\
	\n\nQiwi: <b>+{req}</b>\
	\nСумма: <b>{amount} RUB</b>\
	\n\n<i>Администрация проекта рассмотрит вашу заявку, деньги придут по мере нагрузки проекта!</i>"
)

out_done_otz = emojize(
    "<b>Администация проекта одобрила вашу заявку на вывод</b>!\
	\n<i>Пожалуйста предоставьте скриншоты вывода в чат</i> :green_heart:"
)

collect_done = lambda amount: emojize(f":moneybag: Вы собрали {amount:.2f} RUB")

collect_tosmall = emojize(":warning: Минимальная сумма сбора: 1 RUB")

invest_done = lambda amount: emojize(f":moneybag: Вы инвестировали {amount:.2f} RUB")

invest_tosmall = emojize(":warning: Минимальная сумма инвестиции: 100 RUB")

add_unsuccesful = emojize(
    f":warning: Мы не получили Ваш платеж.\
	\nНапишите @{SUPP}, в случае, если считаете, что это - <b>ошибка</b>."
)

add_succesful = lambda amount: emojize(
    f"<a href='https://telegra.ph/file/c1a75613995a1e21e8759.png'>:green_heart:</a>\
	Вы <b>успешно</b> пополнили свой счет на <b>{amount} RUB</b>. <b>Спасибо</b>!"
)

admins_out = lambda cid, amount, req: emojize(
    f"Заявка на вывод :moyai:\
	\nИнфо: <b>{amount} RUB</b>, <b>+{req}</b> [<code>{cid}</code>]"
)
