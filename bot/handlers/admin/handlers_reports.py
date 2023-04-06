from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from app import dp, bot
from bot.handlers import commands
from bot.markups.keyboards_admin import keyboard_reports_list, keyboard_report_admin_action, admin_menu, \
    keyboard_admin_state_cancel
from bot.messages.admin import messages_admin_reports
from bot.states.state_admin import StateReport
from database.models.reports import Report


@dp.callback_query_handler(text_startswith="reports")
async def handler_reports_list(callback: CallbackQuery):
    page = int(callback.data.split('_')[1])
    reports_len = await Report.all().count()
    if reports_len == 0:
        await callback.answer(
            text=messages_admin_reports.message_report_errors[1000]
        )
    elif page > 0 and (page - 1) * 10 < reports_len:
        await callback.message.edit_text(
            text=messages_admin_reports.message_report_select,
            reply_markup=await keyboard_reports_list(
                page=page
            )
        )
    else:
        await callback.answer(
            text=messages_admin_reports.message_report_errors[1300]
        )


@dp.callback_query_handler(text_startswith="select_report")
async def handler_select_report(callback: CallbackQuery):
    data = callback.data.split('_')
    report = await Report.get_or_none(id=int(data[2]))
    if report:
        send_datetime = report.send_datetime
        await callback.message.edit_text(
            text=messages_admin_reports.message_report_info.format(
                report.tg_username,
                send_datetime.strftime("%d.%m.%Y"),
                report.text
            ),
            reply_markup=await keyboard_report_admin_action(
                report_id=report.id
            )
        )
    else:
        await callback.message.edit_text(
            text=messages_admin_reports.message_report_errors[1404],
            reply_markup=await admin_menu()
        )


@dp.callback_query_handler(text_startswith="record_user_answer_")
async def handler_report_ans(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split('_')
    report = await Report.get_or_none(
        id=int(data[4])
    )
    if report:
        if data[3] == "yes":
            await callback.message.edit_text(
                text=messages_admin_reports.message_report_answer_input,
                reply_markup=keyboard_admin_state_cancel
            )
            await state.update_data({"report_id": int(data[4])})
            await state.update_data({"message_id": callback.message.message_id})
            await StateReport.answer.set()
            return
        elif data[3] == "no":
            await callback.message.edit_text(
                text=messages_admin_reports.message_report_answer_admin[0]
            )
            send_datetime = report.send_datetime
            await bot.send_message(
                chat_id=report.tg_id,
                text=messages_admin_reports.message_report_answer_for_user[0].format(
                    send_datetime.strftime("%d.%m.%Y")
                )
            )
            await report.delete()
    else:
        await callback.answer(
            text=messages_admin_reports.message_report_errors[1404]
        )
    await commands.handler_admin_menu(
        callback=callback,
        state=state
    )


@dp.message_handler(state=StateReport.answer)
async def state_report_answer_input(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=data['message_id']
        )
    except:
        pass
    report = await Report.get_or_none(
        id=data["report_id"]
    )
    if report:
        await message.answer(
            text=messages_admin_reports.message_report_answer_admin[1]
        )
        send_datetime = report.send_datetime
        await bot.send_message(
            chat_id=report.tg_id,
            text=messages_admin_reports.message_report_answer_for_user[1].format(
                send_datetime.strftime("%d.%m.%Y"),
                message.text
            )
        )
        await report.delete()
    else:
        await message.answer(
            text=messages_admin_reports.message_report_errors[1404]
        )
