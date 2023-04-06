from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaDocument

from bot.markups.keyboards_user import keyboard_state_cancel, main_menu_keyboard, keyboard_lots_list, \
    keyboard_lot_action
from bot.messages.user import messages_lots
from bot.states.state_user import StateUserLot

from configuration import config
from database.models.lots import Lot
from database.models.lots_cache import LotCache
from app import dp, bot
from database.models.user import User


@dp.callback_query_handler(text_startswith="get_lots_", state='*')
async def handler_lots_list(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    user = await User.get_or_none(
        tg_id=callback.from_user.id,
        is_banned=False
    )
    if user:
        if user.verification == 1:
            data = callback.data.split('_')
            page = int(data[2])
            if await Lot.filter(is_active=True).count() == 0:
                await callback.answer(
                    text=messages_lots.message_lots_error[0]
                )
            elif page > 0 and (page - 1) * 10 < await Lot.filter(is_active=True).count():
                await callback.message.edit_text(
                    text=messages_lots.message_lots_menu.format(
                        callback.message.date.strftime("%d.%m.%Y")
                    ),
                    reply_markup=await keyboard_lots_list(
                        page=page
                    )
                )
            else:
                await callback.answer(
                    text=messages_lots.message_lots_error[-1]
                )
        else:
            await callback.answer(
                text=messages_lots.message_verification_error
            )


@dp.callback_query_handler(text_startswith="handler_lot_", state='*')
async def handler_lot_info(callback: CallbackQuery, state: FSMContext):
    user = await User.get_or_none(
        tg_id=callback.from_user.id,
        is_banned=False
    )
    if user:
        if user.verification == 1:
            data = callback.data.split('_')
            lot = await Lot.get_or_none(
                id=data[2]
            )
            if lot:
                await callback.message.delete()
                if lot.media_type:
                    state_data = await state.get_data()
                    if "media_messages" in state_data:
                        for media_message in state_data['media_messages']:
                            await bot.delete_message(
                                chat_id=callback.from_user.id,
                                message_id=media_message.message_id
                            )
                    media = [InputMediaDocument(i) for i in lot.media.split(";")]
                    media_messages = await bot.send_media_group(
                        chat_id=callback.from_user.id,
                        media=media
                    )
                    await state.update_data(media_messages=media_messages)
                first_last_price = messages_lots.first_last_price[0].format(
                    lot.first_price
                ) if lot.last_price == 0 else messages_lots.first_last_price[1].format(
                    lot.last_price
                )
                await callback.message.answer(
                    text=messages_lots.message_lot_info.format(
                        lot.id, lot.post_datetime.strftime("%d.%m.%Y %H:%M"),
                        lot.location,
                        lot.task,
                        lot.deadline,
                        first_last_price
                    ),
                    reply_markup=await keyboard_lot_action(lot_id=lot.id)
                )
            else:
                await callback.answer(
                    text=messages_lots.message_lots_error[1]
                )
        else:
            await callback.answer(
                text=messages_lots.message_verification_error
            )


@dp.callback_query_handler(text_startswith="lot_lower_", state='*')
async def handler_lot_action(callback: CallbackQuery, state: FSMContext):
    user = await User.get_or_none(
        tg_id=callback.from_user.id,
        is_banned=False
    )
    if user:
        if user.verification == 1:
            data = callback.data.split('_')
            lot = await Lot.get_or_none(
                id=data[2]
            )
            if lot:
                lot_price = lot.first_price if lot.last_price == 0 else lot.last_price
                if data[3] != "state":
                    await state.finish()
                    lot.last_price = int(lot_price * float(data[3]))
                    if lot.last_price > config["MINIMUM_PRICE"]:
                        await LotCache.create(
                            lot_id=lot.id,
                            tg_id=callback.from_user.id,
                            price=lot.last_price
                        )
                        await lot.save()
                        await callback.message.edit_text(
                            text=messages_lots.message_lot_info.format(
                                lot.id, lot.post_datetime.strftime("%d.%m.%Y %M:%H"),
                                lot.location,
                                lot.task,
                                lot.deadline,
                                messages_lots.first_last_price[1].format(lot.last_price)
                            ),
                            reply_markup=await keyboard_lot_action(lot_id=lot.id)
                        )
                        await callback.answer(
                            text=messages_lots.message_lot_answer
                        )
                    else:
                        await callback.answer(
                            text=messages_lots.message_lots_error[2].format(
                                config["MINIMUM_PRICE"], lot_price
                            )
                        )

                else:
                    state_data = await state.get_data()
                    if "media_messages" in state_data:
                        for media_message in state_data['media_messages']:
                            await bot.delete_message(
                                chat_id=callback.from_user.id,
                                message_id=media_message.message_id
                            )
                    await callback.message.edit_text(
                        text=messages_lots.message_lot_price_input.format(
                            config["MINIMUM_PRICE"], lot_price
                        ),
                        reply_markup=keyboard_state_cancel
                    )
                    await state.update_data(message_id=callback.message.message_id)
                    await state.update_data(lot_id=lot.id)
                    await state.update_data(lot_price=lot_price)
                    await StateUserLot.price.set()
            else:
                await state.finish()
                await callback.answer(
                    text=messages_lots.message_lots_error[1]
                )
        else:
            await state.finish()
            await callback.answer(
                text=messages_lots.message_verification_error
            )


@dp.message_handler(state=StateUserLot.price)
async def state_lot_price_input(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=data['message_id']
        )
    except:
        pass
    if message.text.isdigit():
        price = int(message.text)
        if config["MINIMUM_PRICE"] <= price < data['lot_price']:
            await state.finish()
            lot = await Lot.get(id=data['lot_id'])
            lot.last_price = price
            await lot.save()
            await LotCache.create(
                lot_id=lot.id,
                tg_id=message.from_user.id,
                price=price
            )
            if lot.media_type:
                media = [InputMediaDocument(i) for i in lot.media.split(";")]
                media_messages = await bot.send_media_group(
                    chat_id=message.from_user.id,
                    media=media
                )
                await state.update_data(media_messages=media_messages)
            await message.answer(
                text=messages_lots.message_lot_info.format(
                    lot.id, lot.post_datetime.strftime("%d.%m.%Y %M:%H"),
                    lot.location,
                    lot.task,
                    lot.deadline,
                    messages_lots.first_last_price[1].format(lot.last_price)
                ),
                reply_markup=await keyboard_lot_action(lot_id=lot.id)
            )
            return
        else:
            if data['lot_price'] == config['MINIMUM_PRICE']:
                await state.finish()
                await message.answer(
                    text=messages_lots.message_lots_error[3],
                    reply_markup=await main_menu_keyboard(
                        user_id=message.from_user.id
                    )
                )
                return
            mess = await message.answer(
                text=messages_lots.message_lots_error[2].format(
                    config["MINIMUM_PRICE"], data['lot_price']
                )
            )
    else:
        mess = await message.answer(
            text=messages_lots.message_isdigit_error,
            reply_markup=keyboard_state_cancel
        )
    await state.update_data(message_id=mess.message_id)
