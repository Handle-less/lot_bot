from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from app import dp, bot
from bot.handlers import commands
from bot.markups.keyboards_admin import keyboard_admin_state_cancel, keyboard_dist_menu, admin_menu
from bot.messages.admin import messages_admin_dist
from bot.states.state_admin import StateDist
from database.models.user import User


@dp.callback_query_handler(text_startswith="send_dist")
async def call_dist_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=messages_admin_dist.message_state_dist_text_input,
        reply_markup=keyboard_admin_state_cancel
    )
    await state.update_data({"message_id": callback.message.message_id})
    await StateDist.text.set()


@dp.callback_query_handler(text_startswith="dist_")
async def call_dist_menu(callback: CallbackQuery, state: FSMContext):
    if callback.data == "dist_add":
        if callback.message.text:
            await callback.message.edit_text(
                text=messages_admin_dist.message_state_dist_preview_input,
                reply_markup=keyboard_admin_state_cancel
            )
            await state.update_data(
                {
                    "text": callback.message.text,
                    "message_id": callback.message.message_id
                }
            )
            await StateDist.preview.set()
        else:
            await callback.answer(
                text=messages_admin_dist.message_dist_errors[101]
            )
    elif callback.data == "dist_del":
        if not callback.message.text:
            await callback.message.delete()
            await bot.send_message(
                chat_id=callback.from_user.id,
                text=callback.message.caption,
                reply_markup=await keyboard_dist_menu()
            )
        else:
            await callback.answer(
                text=messages_admin_dist.message_dist_errors[100]
            )
    elif callback.data == "dist_see":
        await bot.forward_message(callback.from_user.id, callback.from_user.id, callback.message.message_id)
    elif callback.data == "dist_start":
        await callback.message.edit_reply_markup()
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=messages_admin_dist.message_dist_start
        )
        users = await User.filter(is_banned=False)
        good = 0
        bad = 0
        for user in users:
            try:
                await bot.forward_message(chat_id=user.tg_id,
                                          from_chat_id=callback.from_user.id,
                                          message_id=callback.message.message_id)
                good += 1
            except:
                bad += 1
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=messages_admin_dist.message_dist_finish.format(
                good + bad,
                good,
                bad
            ),
            reply_markup=await admin_menu()
        )
    elif callback.data == "dist_cancel":
        await callback.message.delete()
        await commands.handler_admin_menu(
            callback=callback,
            state=state
        )


@dp.message_handler(state=StateDist.text)
async def state_adm_dist_text(message: Message, state: FSMContext):
    message_id = (await state.get_data())["message_id"]
    await state.finish()
    await bot.edit_message_reply_markup(chat_id=message.from_id, message_id=message_id)
    await message.answer(text=message.text,
                         reply_markup=await keyboard_dist_menu())


@dp.message_handler(state=StateDist.preview, content_types=[ContentType.PHOTO,
                                                            ContentType.VIDEO,
                                                            ContentType.ANIMATION]
                    )
async def state_adm_dist_preview(message: Message, state: FSMContext):
    message_id = (await state.get_data())["message_id"]
    text = (await state.get_data())["text"]
    await state.finish()
    await bot.edit_message_reply_markup(chat_id=message.from_id, message_id=message_id)
    if message.photo:
        await bot.send_photo(chat_id=message.from_id,
                             photo=message.photo[-1].file_id,
                             caption=text,
                             reply_markup=await keyboard_dist_menu())
    elif message.video:
        await bot.send_video(chat_id=message.from_id,
                             video=message.video.file_id,
                             caption=text,
                             reply_markup=await keyboard_dist_menu())
    elif message.animation:
        await bot.send_animation(chat_id=message.from_id,
                                 animation=message.animation.file_id,
                                 caption=text,
                                 reply_markup=await keyboard_dist_menu())
