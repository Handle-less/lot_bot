from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.markups.keyboards_admin import keyboard_user_list, keyboard_admin_user_menu, keyboard_admin_state_cancel
from bot.messages.admin import messages_admin_users_list
from bot.states.state_admin import StateUser

from database.models.user import User

from app import dp, bot


@dp.callback_query_handler(text_startswith="users_list")
async def call_users_list(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    data = callback.data.split('_')
    if data[2] != "state":
        all_users = await User.filter().count()
        verified_users = await User.filter(verification=1).count()
        banned_users = await User.filter(is_banned=True).count()
        page = int(data[2])
        if page > 0 and (page - 1) * 10 < all_users:
            await callback.message.edit_text(
                text=messages_admin_users_list.message_menu_admin.format(
                    all_users,
                    verified_users,
                    banned_users
                ),
                reply_markup=await keyboard_user_list(
                    page=page
                )
            )
        else:
            await callback.answer(
                text=messages_admin_users_list.message_menu_errors[1300]
            )
    else:
        await callback.message.edit_text(
            text=messages_admin_users_list.message_user_input,
            reply_markup=keyboard_admin_state_cancel
        )
        await state.update_data(message_id=callback.message.message_id)
        await StateUser.name_or_id.set()


@dp.message_handler(state=StateUser.name_or_id)
async def state_user_input(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=data['message_id']
        )
    except:
        pass
    if message.text.isdigit():
        user = await User.get_or_none(tg_id=message.text)
    else:
        user = await User.get_or_none(tg_username=message.text)
    if user:
        await state.finish()
        message_menu_errors = messages_admin_users_list.message_menu_errors
        await message.answer(
            text=messages_admin_users_list.message_user_info.format(
                user.tg_id,
                user.tg_username,
                message_menu_errors[user.is_banned],
                message_menu_errors[user.verification],
                user.reg_date.strftime("%d.%m.%Y")
            ),
            reply_markup=await keyboard_admin_user_menu(
                user=user
            )
        )
    else:
        mess = await message.answer(
            text=messages_admin_users_list.message_menu_errors[1404],
            reply_markup=keyboard_admin_state_cancel
        )
        await state.update_data(message_id=mess.message_id)


@dp.callback_query_handler(text_startswith="handler_user_action_")
async def handler_admin_user_action(callback: CallbackQuery):
    data = callback.data.split('_')
    user = await User.get(tg_id=data[3])
    message_menu_errors = messages_admin_users_list.message_menu_errors
    await callback.message.edit_text(
        text=messages_admin_users_list.message_user_info.format(
            user.tg_id,
            user.tg_username,
            message_menu_errors[user.is_banned],
            message_menu_errors[user.verification],
            user.reg_date.strftime("%d.%m.%Y")
        ),
        reply_markup=await keyboard_admin_user_menu(
            user=user
        )
    )


@dp.callback_query_handler(text_startswith="edit_user_")
async def handler_admin_user_action(callback: CallbackQuery):
    data = callback.data.split('_')
    user = await User.get(tg_id=data[3])
    if data[2] == "verif":
        user.verification = 1 if user.verification == -1 else int(not user.verification)
    elif data[2] == "ban":
        user.is_banned = int(not user.is_banned)
    await user.save()
    message_menu_errors = messages_admin_users_list.message_menu_errors
    await callback.message.edit_text(
        text=messages_admin_users_list.message_user_info.format(
            user.tg_id,
            user.tg_username,
            message_menu_errors[user.is_banned],
            message_menu_errors[user.verification],
            user.reg_date.strftime("%d.%m.%Y")
        ),
        reply_markup=await keyboard_admin_user_menu(
            user=user
        )
    )



# @dp.callback_query_handler(text_startswith="handler_user_action")
# async def call_select_user(call: CallbackQuery):
#     user = get_user(call.data.split('_')[2])
#     if int(user[6]) > int(time()):
#         end_time = gmtime(int(user[6]))
#         end_time = f"{user[5]} | до {end_time.tm_mday}-{end_time.tm_mon}-{end_time.tm_year}"
#     else:
#         end_time = "нет доступа"
#     await call.message.edit_text(text=f"@{user[1]} | {user[0]} | {end_time}\n"
#                                       f"Он с нами с {user[2]}",
#                                  reply_markup=menu_user(user))
#
#
# @dp.callback_query_handler(text_startswith="edit_user")
# async def call_edit_user(call: CallbackQuery, state: FSMContext):
#     data = call.data.split('_')
#     user = get_user(data[3])
#     if data[2] == "days":
#         await call.message.edit_text(text="Введите количество дней\n"
#                                           "(например 1 что бы прибавить 1 день и -1 что бы убрать 1 день)",
#                                      reply_markup=cancel_adm_state())
#         await state.update_data({"id_message": call.message.message_id,
#                                  "user_id": data[3]})
#         await EditUser.days.set()
#     elif data[2] == "ban":
#         if not user[4]:
#             set_user_ban(user[0], 1)
#             await call.answer(text="Пользователь заблокирован")
#         else:
#             set_user_ban(user[0], 0)
#             await call.answer(text="Пользователь разблокирован")
#         try:
#             await call.message.edit_reply_markup(reply_markup=menu_user(get_user(user[0])))
#         except:
#             pass