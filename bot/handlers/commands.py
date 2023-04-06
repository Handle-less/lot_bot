from aiogram.types import Message, ChatType, ReplyKeyboardMarkup, KeyboardButton, ContentType, CallbackQuery
from aiogram.dispatcher import FSMContext

from bot.markups.keyboards_user import main_menu_keyboard
from bot.markups.keyboards_admin import admin_menu
from bot.messages.user import messages_start
from bot.states.state_user import StartState

from database.models.user import User
from app import dp


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=['start'], state='*')
async def command_start(message: Message, state: FSMContext):
    await state.finish()
    user = await User.get_or_none(tg_id=message.from_user.id)
    if not user and message.from_user.username:
        await message.answer(
            text=messages_start.input_full_name_message
        )
        await StartState.full_name.set()
    elif not message.from_user.username:
        await message.answer(
            text=messages_start.username_error
        )
    else:
        if not user.is_banned:
            await message.answer(
                text=messages_start.start_message.format(
                    user.full_name,
                    user.tg_id,
                    messages_start.verification_text[user.verification],
                    user.balance
                ),
                reply_markup=await main_menu_keyboard(
                    user_id=message.from_user.id
                )
            )


@dp.message_handler(state=StartState.full_name)
async def state_input_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    kb = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    kb.add(KeyboardButton("Поделиться номером телефона", request_contact=True))

    await message.answer(
        text=messages_start.input_phone_message,
        reply_markup=kb
    )
    await StartState.next()


@dp.message_handler(state=StartState.phone, content_types=[
    ContentType.TEXT,
    ContentType.CONTACT
]
                    )
async def state_input_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    user = await User.create(
        tg_id=message.from_user.id,
        tg_username=message.from_user.username,
        full_name=data['full_name'],
        phone=message.text if message.text else message.contact.phone_number,
        reg_date=message.date
    )
    await message.answer(
        text=messages_start.start_message.format(
            user.full_name,
            user.tg_id,
            messages_start.verification_text[user.verification],
            user.balance
        ),
        reply_markup=await main_menu_keyboard(
            user_id=message.from_user.id
        )
    )


@dp.callback_query_handler(text="admin", state='*')
async def handler_admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text(
        text="Админ панель",
        reply_markup=await admin_menu()
    )


@dp.callback_query_handler(text="back_to_main_menu", state='*')
async def handler_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    user = await User.get_or_none(
        tg_id=callback.from_user.id,
        is_banned=False
    )
    if user:
        await callback.message.edit_text(
            text=messages_start.start_message.format(
                user.full_name,
                user.tg_id,
                messages_start.verification_text[user.verification],
                user.balance
            ),
            reply_markup=await main_menu_keyboard(
                user_id=callback.from_user.id
            )
        )
