from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from configuration import config
from database.models.lots import Lot

back_to_main_menu_button = InlineKeyboardButton("Назад", callback_data="back_to_main_menu")


async def main_menu_keyboard(user_id):
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton("🔐 Пройти верификацию", callback_data="start_verification"),
        InlineKeyboardButton("📈 Участвовать в торгах", callback_data="get_lots_1"),
        InlineKeyboardButton("📨 Контакты", callback_data="contacts")
    ]

    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2).add(*buttons)
    if user_id in config["ADMINS_ID"]:
        keyboard.add(
            InlineKeyboardButton(text="Перейти в админ панель", callback_data="admin")
        )
    return keyboard


async def keyboard_lots_list(page):
    lots_list = await Lot.filter(is_active=True)
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()
    for lot in lots_list[(page-1)*10:page*10]:
        keyboard.add(
            InlineKeyboardButton(
                text=f"Заказ № {lot.id}",
                callback_data=f"handler_lot_{lot.id}"
            )
        )
    buttons = [
        InlineKeyboardButton(text='◀', callback_data=f"get_lots_{page-1}"),
        InlineKeyboardButton(text=f"{page}", callback_data=f"_"),
        InlineKeyboardButton(text='▶', callback_data=f"get_lots_{page+1}")
    ]
    keyboard.add(*buttons).add(back_to_main_menu_button)
    return keyboard


async def keyboard_lot_action(lot_id):
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text='➖', callback_data='_')
        for _ in range(9)
    ]
    text_button = InlineKeyboardButton(text="Дешевле на", callback_data='_')
    but: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text='5%', callback_data=f'lot_lower_{lot_id}_0.95'),
        InlineKeyboardButton(text='10%', callback_data=f'lot_lower_{lot_id}_0.90'),
        InlineKeyboardButton(text='25%', callback_data=f'lot_lower_{lot_id}_0.75')
    ]
    keyboard = InlineKeyboardMarkup(row_width=9).add(text_button).add(*but).add(
        InlineKeyboardButton(text='Предложить стоимость', callback_data=f'lot_lower_{lot_id}_state')
    ).add(*buttons).add(
        InlineKeyboardButton(text="Обновить🔄", callback_data=f"handler_lot_{lot_id}")
    ).add(
        InlineKeyboardButton("Вернуться в меню", callback_data="back_to_main_menu")
    )
    return keyboard


async def keyboard_lot_notification(lot_id):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='Открыть',
            callback_data=f"handler_lot_{lot_id}"
        )
    )
    return keyboard


contacts_buttons: list[InlineKeyboardButton] = [
    InlineKeyboardButton("Связаться с поддержкой", url=config["SUPPORT_LINK"]),
    InlineKeyboardButton("Задать вопрос", callback_data="send_report"),
    InlineKeyboardButton("Следить за новостями", url=config["NEWS_CHANEL_LINK"]),
    back_to_main_menu_button]

contacts_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1).add(*contacts_buttons)

keyboard_state_cancel = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Вернуться в меню", callback_data="back_to_main_menu")
)
