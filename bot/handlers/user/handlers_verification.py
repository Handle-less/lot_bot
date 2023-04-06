from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.markups.keyboards_admin import verification_user_answer_keyboard
from bot.markups.keyboards_user import keyboard_state_cancel, main_menu_keyboard
from bot.messages.user import messages_verification
from bot.states.state_user import StateVerification

from configuration import config
from app import dp, bot
from database.models.user import User


@dp.callback_query_handler(text="start_verification", state='*')
async def handler_verification_start(callback: CallbackQuery, state: FSMContext):
    user = await User.get_or_none(
        tg_id=callback.from_user.id,
        is_banned=False
    )
    if user:
        if user.verification == 0:
            message = await callback.message.edit_text(
                text=messages_verification.message_uid_input,
                reply_markup=keyboard_state_cancel
            )
            await state.update_data(message_id=message.message_id)
            await StateVerification.uid.set()
        else:
            await callback.answer(
                text=messages_verification.messages_verification_error[user.verification]
            )


@dp.message_handler(state=StateVerification.uid)
async def state_verification_uid_input(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=data["message_id"]
        )
    except:
        pass
    mess = await message.answer(
        text=messages_verification.message_region_input
    )
    await state.update_data(message_id=mess.message_id)
    await state.update_data(uid=message.text)
    await StateVerification.next()


@dp.message_handler(state=StateVerification.region)
async def state_verification_region_input(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=data["message_id"]
        )
    except:
        pass
    mess = await message.answer(
        text=messages_verification.message_category_input
    )
    await state.update_data(message_id=mess.message_id)
    await state.update_data(region=message.text)
    await StateVerification.next()


@dp.message_handler(state=StateVerification.category)
async def state_verification_category_input(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=data['message_id']
        )
    except:
        pass
    user = await User.get(tg_id=message.from_user.id)
    user.verification = -1
    await user.save()
    await bot.send_message(
        chat_id=config["CHAT_FOR_ADMIN_MESSAGES"],
        text=messages_verification.message_admin_notification.format(
            message.from_user.username,
            data['uid'],
            data['region'],
            message.text
        ),
        reply_markup=await verification_user_answer_keyboard(
            user_id=message.from_user.id
        )
    )
    await message.answer(
        text=messages_verification.messages_verification_sent,
        reply_markup=await main_menu_keyboard(
            user_id=message.from_user.id
        )
    )


@dp.callback_query_handler(text_startswith="verification_answer_", state='*')
async def handler_verification_answer(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    data = callback.data.split('_')
    user = await User.get(tg_id=int(data[3]))
    match data[2]:
        case "yes":
            user.verification = 1
            await user.save()
            await callback.message.edit_text(
                text=messages_verification.messages_verification_answer[111].format(
                    callback.message.text
                )
            )
            await bot.send_message(
                chat_id=data[3],
                text=messages_verification.messages_verification_answer[101]
            )
        case "no":
            await callback.message.edit_text(
                text=messages_verification.messages_verification_answer[110].format(
                    callback.message.text
                )
            )
            await bot.send_message(
                chat_id=data[3],
                text=messages_verification.messages_verification_answer[100]
            )
