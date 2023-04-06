from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType, InputMediaDocument

from bot.markups.keyboards_admin import keyboard_admin_state_cancel, keyboard_lot_add_action, admin_menu
from bot.markups.keyboards_user import keyboard_lot_notification
from bot.messages.admin import messages_admin_lot_add

from app import dp, bot
from bot.states.state_admin import StateLotAdd
from configuration import config
from database.models.lots import Lot
from database.models.user import User


@dp.callback_query_handler(text="lot_admin_add", state='*')
async def handler_lot_add(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=messages_admin_lot_add.message_lot_location_input,
        reply_markup=keyboard_admin_state_cancel
    )
    await state.update_data(message_id=callback.message.message_id)
    await StateLotAdd.location.set()


@dp.message_handler(state=StateLotAdd.location)
async def state_lot_location_input(message: Message, state: FSMContext):
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=(await state.get_data())['message_id']
        )
    except:
        pass
    mess = await message.answer(
        text=messages_admin_lot_add.message_lot_task_input,
        reply_markup=keyboard_admin_state_cancel
    )
    await state.update_data(message_id=mess.message_id)
    await state.update_data(location=message.text)
    await StateLotAdd.next()


@dp.message_handler(state=StateLotAdd.task)
async def state_lot_task_input(message: Message, state: FSMContext):
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=(await state.get_data())['message_id']
        )
    except:
        pass
    mess = await message.answer(
        text=messages_admin_lot_add.message_lot_deadline_input,
        reply_markup=keyboard_admin_state_cancel
    )
    await state.update_data(message_id=mess.message_id)
    await state.update_data(task=message.text)
    await StateLotAdd.next()


@dp.message_handler(state=StateLotAdd.deadline)
async def state_lot_deadline_input(message: Message, state: FSMContext):
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=(await state.get_data())['message_id']
        )
    except:
        pass
    mess = await message.answer(
        text=messages_admin_lot_add.message_lot_price_input,
        reply_markup=keyboard_admin_state_cancel
    )
    await state.update_data(message_id=mess.message_id)
    await state.update_data(deadline=message.text)
    await StateLotAdd.next()


@dp.message_handler(state=StateLotAdd.first_price)
async def state_lot_price_input(message: Message, state: FSMContext):
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=(await state.get_data())['message_id']
        )
    except:
        pass
    if message.text.isdigit() and int(message.text) >= config["MINIMUM_PRICE"]:
        data = await state.get_data()
        await state.update_data(price=int(message.text))
        await state.update_data(media_type=None)
        await state.update_data(media=None)

        mess = await message.answer(
            text=messages_admin_lot_add.message_lot_add_info.format(
                data['location'],
                data['task'],
                data['deadline'],
                message.text
            ),
            reply_markup=await keyboard_lot_add_action()
        )
        await StateLotAdd.next()
    else:
        mess = await message.answer(
            text=messages_admin_lot_add.message_lot_add_error['value'].format(
                config["MINIMUM_PRICE"]
            ),
            reply_markup=keyboard_admin_state_cancel
        )
    await state.update_data(message_id=mess.message_id)


@dp.callback_query_handler(text_startswith="handler_admin_lot_edit_", state=StateLotAdd.state_action)
async def handler_lot_edit(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split('_')
    state_data = await state.get_data()
    match data[4]:
        case "file":
            await callback.message.edit_text(
                text=messages_admin_lot_add.message_lot_file_input
            )
            await state.update_data(state_step='file')
            await StateLotAdd.state_edit.set()
        case "file!delete":
            if state_data['media_type'] is not None:
                await state.update_data(media_type=None)
                await state.update_data(media=None)
                await callback.answer(
                    text=messages_admin_lot_add.message_lot_file_deleted
                )
            else:
                await callback.answer(
                    text=messages_admin_lot_add.message_lot_file_errors[1404]
                )
        case "location":
            await callback.message.edit_text(
                text=messages_admin_lot_add.message_lot_location_input
            )
            await state.update_data(state_step='location')
            await StateLotAdd.state_edit.set()
        case "task":
            await callback.message.edit_text(
                text=messages_admin_lot_add.message_lot_task_input
            )
            await state.update_data(state_step='task')
            await StateLotAdd.state_edit.set()
        case "deadline":
            await callback.message.edit_text(
                text=messages_admin_lot_add.message_lot_deadline_input
            )
            await state.update_data(state_step='deadline')
            await StateLotAdd.state_edit.set()
        case "price":
            await callback.message.edit_text(
                text=messages_admin_lot_add.message_lot_price_input
            )
            await state.update_data(state_step='price')
            await StateLotAdd.state_edit.set()
        case "send":
            lot = await Lot.create(
                post_datetime=datetime.now(),
                media_type=state_data["media_type"],
                media=state_data["media"],
                location=state_data['location'],
                task=state_data['task'],
                deadline=state_data['deadline'],
                first_price=state_data['price'],
            )
            await state.finish()
            await callback.message.edit_text(
                text=messages_admin_lot_add.message_lot_send,
                reply_markup=await admin_menu()
            )

            users = await User.filter(is_banned=0, verification=1)
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.tg_id,
                        text=messages_admin_lot_add.message_new_lot_notification.format(
                            lot.id,
                            lot.location
                        ),
                        reply_markup=await keyboard_lot_notification(lot.id)
                    )
                except:
                    pass


@dp.message_handler(state=StateLotAdd.state_edit, content_types=[ContentType.DOCUMENT,
                                                                 ContentType.TEXT])
async def state_lot_edit_input(message: Message, state: FSMContext):
    data = await state.get_data()
    match data['state_step']:
        case "file":
            if message.document:
                await state.update_data(media_type=message.content_type)
                if data['media']:
                    media = data['media'].split(';')
                    media.append(message.document.file_id)
                    await state.update_data(media=';'.join(media))
                else:
                    await state.update_data(media=message.document.file_id)
        case "location":
            await state.update_data(location=message.text)
        case "task":
            await state.update_data(task=message.text)
        case "deadline":
            await state.update_data(deadline=message.text)
        case "price":
            if message.text.isdigit() and int(message.text) >= config["MINIMUM_PRICE"]:
                await state.update_data(price=int(message.text))
            else:
                await message.answer(
                    text=messages_admin_lot_add.message_lot_add_error['value'].format(
                        config["MINIMUM_PRICE"]
                    )
                )
                return
    data = await state.get_data()
    if data["media_type"]:
        media = [InputMediaDocument(i) for i in data["media"].split(";")]
        await bot.send_media_group(
            chat_id=message.from_user.id,
            media=media
        )
    await message.answer(
        text=messages_admin_lot_add.message_lot_add_info.format(
            data['location'],
            data['task'],
            data['deadline'],
            data['price']
        ),
        reply_markup=await keyboard_lot_add_action()
    )
    await StateLotAdd.state_action.set()
