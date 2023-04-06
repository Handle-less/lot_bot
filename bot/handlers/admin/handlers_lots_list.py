from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from bot.handlers.commands import handler_admin_menu

from bot.markups.keyboards_admin import keyboard_lots_list, keyboard_lot_action, keyboard_lot_winners
from bot.messages.admin import messages_admin_lots

from database.models.lots import Lot

from app import dp, bot
from database.models.lots_cache import LotCache
from database.models.user import User


@dp.callback_query_handler(text_startswith="admin_lot_list_", state="*")
async def handler_lot_admin_list(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    try:
        data = callback.data.split('_')
        is_active = int(data[3])
        all_lots = await Lot.filter(is_active=is_active).count()
        page = int(data[4])
        if all_lots == 0:
            all_lots = await Lot.filter(is_active=not is_active).count()
            if all_lots:
                await callback.message.edit_text(
                    text=messages_admin_lots.message_lot_menu_list,
                    reply_markup=await keyboard_lots_list(
                        is_active=not is_active,
                        page=1
                    )
                )
            else:
                await callback.answer(
                    text=messages_admin_lots.lots_menu_errors[1300]
                )
        elif page > 0 and (page - 1) * 10 < all_lots:
            await callback.message.edit_text(
                text=messages_admin_lots.message_lot_menu_list,
                reply_markup=await keyboard_lots_list(
                    is_active=is_active,
                    page=page
                )
            )
        else:
            await callback.answer(
                text=messages_admin_lots.lots_menu_errors[-1]
            )
    except Exception as e:
        await callback.answer(
            text=messages_admin_lots.lots_menu_errors[1300]
        )


@dp.callback_query_handler(text_startswith="admin_handler_lot_", state='*')
async def handler_lot_info(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    data = callback.data.split('_')
    lot = await Lot.get_or_none(id=int(data[3]))
    if lot:
        if lot.is_active:
            first_last_price = messages_admin_lots.first_last_price[0].format(
                lot.first_price
            ) if lot.last_price == 0 else messages_admin_lots.first_last_price[1].format(
                lot.last_price
            )
            await callback.message.edit_text(
                text=messages_admin_lots.message_active_lot_menu_info.format(
                    lot.id, lot.post_datetime.strftime("%d.%m.%Y %H:%M"),
                    lot.location,
                    lot.task,
                    lot.deadline,
                    first_last_price
                ),
                reply_markup=await keyboard_lot_action(
                    lot_id=lot.id,
                    is_active=lot.is_active
                )
            )
        else:
            lot_cache = await LotCache.get(id=lot.winner_id)
            user = await User.get(tg_id=lot_cache.tg_id)
            await callback.message.edit_text(
                text=messages_admin_lots.message_inactive_lot_menu_info.format(
                    lot.id, lot.post_datetime.strftime("%d.%m.%Y %H:%M"),
                    lot.location,
                    lot.task,
                    lot.deadline,
                    user.tg_id,
                    user.tg_username,
                    user.full_name,
                    user.phone,
                    lot_cache.price
                ),
                reply_markup=await keyboard_lot_action(
                    lot_id=lot.id,
                    is_active=lot.is_active
                )
            )
    else:
        await callback.answer(
            text=messages_admin_lots.lots_menu_errors[1404]
        )


@dp.callback_query_handler(text_startswith="admin_lot_", state='*')
async def handler_lot_action(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    data = callback.data.split('_')
    lot = await Lot.get_or_none(id=int(data[3]))
    if lot:
        if data[2] == "winner":
            lot_cache = await LotCache.filter(lot_id=lot.id).count()
            page = int(data[4])
            if lot_cache == 0:
                await callback.answer(
                    text=messages_admin_lots.lots_menu_errors[1330]
                )
            elif page > 0 and (page - 1) * 10 < lot_cache:
                await callback.message.edit_text(
                    text=messages_admin_lots.message_lot_select_winner,
                    reply_markup=await keyboard_lot_winners(
                        lot_id=lot.id,
                        page=page
                    )
                )
            else:
                await callback.answer(
                    text=messages_admin_lots.lots_menu_errors[-1]
                )
        else:
            await LotCache.filter(lot_id=lot.id).delete()
            await lot.delete()
            await callback.answer(
                text=messages_admin_lots.message_lot_deleted
            )
            await handler_admin_menu(
                callback=callback,
                state=state
            )


@dp.callback_query_handler(text_startswith="lot_end_", state='*')
async def handler_lot_end(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    data = callback.data.split('_')
    lot_cache = await LotCache.get_or_none(id=int(data[2]))
    if lot_cache:
        lot = await Lot.get(id=lot_cache.lot_id)
        lot.is_active = 0
        lot.winner_id = lot_cache.id
        lot.end_datetime = datetime.now()
        user = await User.get(tg_id=lot_cache.tg_id)
        user.balance += lot_cache.price
        await callback.answer(
            text=messages_admin_lots.message_lot_admin_end
        )
        await handler_admin_menu(
            callback=callback,
            state=state
        )
        await bot.send_message(
            chat_id=lot_cache.tg_id,
            text=messages_admin_lots.message_lot_user_end.format(
                lot_cache.lot_id,
                lot_cache.price
            )
        )
        await lot.save()
        await user.save()
    else:
        await callback.answer(
            text=messages_admin_lots.lots_menu_errors[1404]
        )
        await handler_admin_menu(
            callback=callback,
            state=state
        )
