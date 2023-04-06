import logging
from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.markups.keyboards_admin import record_user_answer_keyboard
from bot.markups.keyboards_user import contacts_keyboard, keyboard_state_cancel, main_menu_keyboard
from bot.messages.user import messages_contacts
from bot.states.state_user import StateReport

from configuration import config
from database.models.reports import Report
from app import dp, bot
from database.models.user import User


@dp.callback_query_handler(text="contacts", state='*')
async def handler_contacts(callback: CallbackQuery, state: FSMContext):
    if await User.get_or_none(
            tg_id=callback.from_user.id,
            is_banned=False
    ):
        await state.finish()
        await callback.message.edit_text(
            text=messages_contacts.message_contacts_menu,
            reply_markup=contacts_keyboard
        )


@dp.callback_query_handler(text="send_report", state='*')
async def handler_report_send(callback: CallbackQuery, state: FSMContext):
    if await User.get_or_none(
            tg_id=callback.from_user.id,
            is_banned=False
    ):
        message = await callback.message.edit_text(
            text=messages_contacts.report_message_input,
            reply_markup=keyboard_state_cancel
        )
        await state.update_data(message_id=message.message_id)
        await StateReport.text.set()


@dp.message_handler(state=StateReport.text)
async def state_report_text_input(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=data['message_id']
        )
    except:
        pass
    report = await Report.create(
        tg_id=message.from_user.id,
        tg_username=message.from_user.username,
        send_datetime=datetime.now(),
        text=message.text
    )
    for admin in config["ADMINS_ID"]:
        try:
            await bot.send_message(
                chat_id=admin,
                text=messages_contacts.message_report_admin_notification.format(
                    message.from_user.username,
                    message.text
                ),
                reply_markup=await record_user_answer_keyboard(report.id)
            )
        except Exception as e:
            logging.info(f"ERROR 1404: Can't find admin id = '{admin}' in bot usages\n"
                         f"{e}")

    await message.answer(
        text=messages_contacts.message_report_sent,
        reply_markup=await main_menu_keyboard(
            user_id=message.from_user.id
        )
    )
