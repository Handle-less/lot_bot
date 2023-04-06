from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.messages.admin import messages_admin_users_list
from database.models.lots import Lot
from database.models.lots_cache import LotCache
from database.models.reports import Report
from database.models.user import User


async def admin_menu():
    kb = InlineKeyboardMarkup(row_width=2)

    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton("👥 Пользователи", callback_data="users_list_1"),
        InlineKeyboardButton("📨 Рассылка", callback_data="send_dist"),
        InlineKeyboardButton("❓ Вопросы", callback_data="reports_1"),
        InlineKeyboardButton("Список лотов", callback_data="admin_lot_list_1_1"),
        InlineKeyboardButton("➕ Добавить лот", callback_data="lot_admin_add"),
    ]

    kb.add(*buttons).add(
        InlineKeyboardButton("Выйти из админ панели", callback_data="back_to_main_menu")
    )
    return kb


async def keyboard_user_list(page):
    kb = InlineKeyboardMarkup()
    users = await User.filter()
    verif_text = {
        1: "Верифицирован",
        0: "Не верифицирован",
        -1: "На проверке"
    }
    for user in users:
        kb.add(
            InlineKeyboardButton(
                text=f"@{user.tg_username} | {user.tg_id} | {verif_text[user.verification]}",
                callback_data=f'handler_user_action_{user.tg_id}'
            )
        )
    buttons = [
        InlineKeyboardButton(text='◀', callback_data=f"users_list_{page - 1}"),
        InlineKeyboardButton(text=f"{page}", callback_data=f"_"),
        InlineKeyboardButton(text='▶', callback_data=f"users_list_{page + 1}")
    ]
    kb.add(*buttons)
    search = InlineKeyboardButton("Поиск пользователя", callback_data="users_list_state")
    back = InlineKeyboardButton("Назад", callback_data="admin")
    kb.add(search).add(back)
    return kb


async def keyboard_admin_user_menu(user: User):
    kb = InlineKeyboardMarkup(row_width=2)
    message_menu_errors = messages_admin_users_list.message_menu_errors

    buttons = [
        InlineKeyboardButton(
            text=message_menu_errors[f"2{user.verification}"],
            callback_data=f"edit_user_verif_{user.tg_id}"
        ),
        InlineKeyboardButton(
            text=message_menu_errors[f"1{user.is_banned}"],
            callback_data=f"edit_user_ban_{user.tg_id}"
        ),
        InlineKeyboardButton("Назад", callback_data="users_list_1")
    ]
    kb.add(*buttons)
    return kb


async def keyboard_dist_menu():
    kb = InlineKeyboardMarkup(row_width=2)

    but1 = InlineKeyboardButton("Добавить превью", callback_data="dist_add")
    but2 = InlineKeyboardButton("Удалить превью", callback_data="dist_del")
    but3 = InlineKeyboardButton("Получить результат рассылки", callback_data="dist_see")
    but4 = InlineKeyboardButton("Начать рассылку", callback_data="dist_start")
    but5 = InlineKeyboardButton("Отменить рассылку", callback_data="dist_cancel")

    kb.add(but1, but2).add(but3).add(but4, but5)
    return kb


async def record_user_answer_keyboard(report_id):
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text="Ответить", callback_data=f"record_user_answer_yes_{report_id}"),
        InlineKeyboardButton(text="Отклонить", callback_data=f"record_user_answer_no_{report_id}")
    ]
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup().add(*buttons)
    return keyboard


async def verification_user_answer_keyboard(user_id):
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text="Одобрить", callback_data=f"verification_answer_yes_{user_id}"),
        InlineKeyboardButton(text="Отклонить", callback_data=f"verification_answer_no_{user_id}")
    ]
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup().add(*buttons)
    return keyboard


async def keyboard_reports_list(page):
    kb = InlineKeyboardMarkup()
    reports = await Report.filter()
    for report in reports[(page - 1) * 10:page * 10]:
        kb.add(InlineKeyboardButton(f"@{report.tg_username}", callback_data=f"select_report_{report.id}"))
    buttons = [
        InlineKeyboardButton(text='◀', callback_data=f"reports_{page - 1}"),
        InlineKeyboardButton(text=f"{page}", callback_data=f"_"),
        InlineKeyboardButton(text='▶', callback_data=f"reports_{page + 1}")
    ]
    kb.add(*buttons)
    back = InlineKeyboardButton("Назад", callback_data="admin")
    kb.add(back)
    return kb


async def keyboard_report_admin_action(report_id):
    kb = InlineKeyboardMarkup(row_width=2)

    but1 = InlineKeyboardButton("Ответить", callback_data=f"record_user_answer_yes_{report_id}")
    but2 = InlineKeyboardButton("Отклонить", callback_data=f"record_user_answer_no_{report_id}")
    kb.add(but1, but2)
    back = InlineKeyboardButton("Назад", callback_data="reports_1")
    kb.add(back)

    return kb


async def keyboard_lots_list(is_active, page):
    keyboard = InlineKeyboardMarkup()

    if is_active:
        is_active_buttons = [
            InlineKeyboardButton(text="✅ Активные",
                                 callback_data='_'),
            InlineKeyboardButton(text="Завершённые",
                                 callback_data='admin_lot_list_0_1')
        ]
    else:
        is_active_buttons = [
            InlineKeyboardButton(text="Активные",
                                 callback_data='admin_lot_list_1_1'),
            InlineKeyboardButton(text="✅ Завершённые",
                                 callback_data='_')
        ]
    keyboard.add(*is_active_buttons)
    [
        keyboard.add(InlineKeyboardButton(
            text=f'Лот № {i.id}',
            callback_data=f'admin_handler_lot_{i.id}'
        ))
        for i in await Lot.filter(is_active=is_active)
    ]
    nex_prev_buttons = [
        InlineKeyboardButton(text='◀', callback_data=f"admin_lot_list_{is_active}_{page - 1}"),
        InlineKeyboardButton(text=f"{page}", callback_data=f"_"),
        InlineKeyboardButton(text='▶', callback_data=f"admin_lot_list_{is_active}_{page + 1}")
    ]

    back = InlineKeyboardButton("Назад", callback_data="admin")
    keyboard.add(*nex_prev_buttons).add(back)
    return keyboard


async def keyboard_lot_action(lot_id, is_active):
    buttons = [
        InlineKeyboardButton(
            text="Удалить лот",
            callback_data=f"admin_lot_delete_{lot_id}"
        )
    ]
    if is_active:
        buttons.append(
            InlineKeyboardButton(
                text="Выбрать победителя",
                callback_data=f"admin_lot_winner_{lot_id}_1"
            )
        )
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons).add(
        InlineKeyboardButton(
            text="Назад",
            callback_data=f"admin_lot_list_1_1"
        )
    )
    return keyboard


async def keyboard_lot_winners(lot_id, page):
    keyboard = InlineKeyboardMarkup()
    lot_cache = await LotCache.filter(lot_id=lot_id)
    for lot_user in lot_cache[(page - 1) * 10:page * 10]:
        user = await User.get(tg_id=lot_user.tg_id)
        keyboard.add(InlineKeyboardButton(
            text=f'{lot_user.price}₽ {user.full_name} @{user.tg_username}',
            callback_data=f'lot_end_{lot_user.id}'
        ))
    buttons = [
        InlineKeyboardButton(text='◀', callback_data=f"admin_lot_winner_{lot_id}_{page-1}"),
        InlineKeyboardButton(text=f"{page}", callback_data=f"_"),
        InlineKeyboardButton(text='▶', callback_data=f"admin_lot_winner_{lot_id}_{page+1}")
    ]
    keyboard.add(*buttons)
    back = InlineKeyboardButton("Назад", callback_data=f"admin_handler_lot_{lot_id}")
    keyboard.add(back)
    return keyboard


async def keyboard_lot_add_action():
    buttons = [
        InlineKeyboardButton(
            text="Добавить файл",
            callback_data="handler_admin_lot_edit_file"
        ),
        InlineKeyboardButton(
            text="Очистить файлы",
            callback_data="handler_admin_lot_edit_file!delete"
        ),
        InlineKeyboardButton(
            text="Изменить локацию",
            callback_data="handler_admin_lot_edit_location"
        ),
        InlineKeyboardButton(
            text="Изменить описание",
            callback_data="handler_admin_lot_edit_task"
        ),
        InlineKeyboardButton(
            text="Изменить сроки",
            callback_data="handler_admin_lot_edit_deadline"
        ),
        InlineKeyboardButton(
            text="Изменить цену",
            callback_data="handler_admin_lot_edit_price"
        )
    ]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons).add(
        InlineKeyboardButton(
            text="Опубликовать",
            callback_data="handler_admin_lot_edit_send"
        )
    ).add(
        InlineKeyboardButton(
            text="Отмена",
            callback_data="admin"
        )
    )
    return keyboard


def logs_list(page, logs):
    kb = InlineKeyboardMarkup(row_width=2)
    for log in logs[(page - 1) * 10:page * 10]:
        kb.add(InlineKeyboardButton(f"{log[1]}", callback_data=f"select_edit_log_{log[0]}"))
    if page > 1 and len(logs) - page * 10 > 0:
        but1 = InlineKeyboardButton("⬅", callback_data=f"admin_edit_log_{page - 1}")
        but2 = InlineKeyboardButton("➡", callback_data=f"admin_edit_log_{page + 1}")
        kb.row(but1, but2)
    elif len(logs) - page * 10 > 0:
        but2 = InlineKeyboardButton("➡", callback_data=f"admin_edit_log_{page + 1}")
        kb.add(but2)
    elif page > 1:
        but1 = InlineKeyboardButton("⬅", callback_data=f"admin_edit_log_{page - 1}")
        kb.add(but1)
    back = InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")
    kb.add(back)
    return kb


def edit_log_menu(log):
    kb = InlineKeyboardMarkup(row_width=1)

    but1 = InlineKeyboardButton("Новое количество логов", callback_data=f"edit_log_count_{log}")
    but2 = InlineKeyboardButton("Новая дата логов ", callback_data=f"edit_log_date_{log}")
    but3 = InlineKeyboardButton("Новая ссылка на архив", callback_data=f"edit_log_link_{log}")
    but4 = InlineKeyboardButton("Удалить архив", callback_data=f"edit_log_delete_{log}")
    but5 = InlineKeyboardButton("Выбрать другой архив", callback_data="admin_edit_log_1")
    but6 = InlineKeyboardButton("Выйти в админ меню", callback_data="back_to_admin_menu")

    kb.add(but1, but2, but3, but4, but5, but6)
    return kb


def menu_payment():
    kb = InlineKeyboardMarkup(row_width=1)

    but1 = InlineKeyboardButton("Добавить новый тариф", callback_data="payment_preset_add")
    but2 = InlineKeyboardButton("Редактировать тариф", callback_data="payment_preset_edit")
    back = InlineKeyboardButton("Назад", callback_data="back_to_admin_menu")

    kb.add(but1, but2, back)
    return kb


def menu_edit_payment(search_number):
    kb = InlineKeyboardMarkup(row_width=2)

    but1 = InlineKeyboardButton("Изменить название", callback_data=f"edit_preset_name_{search_number}")
    but2 = InlineKeyboardButton("Изменить кол-во дней", callback_data=f"edit_preset_day_{search_number}")
    but3 = InlineKeyboardButton("Изменить цену", callback_data=f"edit_preset_price_{search_number}")
    but4 = InlineKeyboardButton("Изменить номер тарифа", callback_data=f"edit_preset_num_{search_number}")
    but5 = InlineKeyboardButton("Удалить тариф", callback_data=f"edit_preset_del_{search_number}")
    back = InlineKeyboardButton("Выйти в главное меню", callback_data="back_to_admin_menu")

    kb.add(but1, but2, but3, but4).add(but5).add(back)
    return kb


keyboard_admin_state_cancel = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Вернуться в админ меню", callback_data="admin")
)
