message_lot_menu_list = "Выберите лот"

message_active_lot_menu_info = """
<b>Заказ № {}</b> - {}
<b>Локация:</b> {}
<b>Описание:</b> {}
<b>Сроки:</b> {}
{}
"""

message_inactive_lot_menu_info = """
<b>Заказ № {}</b> - {}
<b>Локация:</b> {}
<b>Описание:</b> {}
<b>Сроки:</b> {}

<b>Победитель:</b>
<b>ID:</b> {}
<b>Link:</b> {}
<b>ФИО:</b> {}
<b>Телефон:</b> {}

<b>Стоимость заказа:</b> {} рублей
"""

first_last_price = {
    0: "<b>Начальная цена:</b> {} рублей",
    1: "<b>Последняя цена:</b> {} рублей"
}

message_lot_select_winner = """
Выберите победителя
"""

message_lot_admin_end = """
Победитель выбран
"""

message_lot_user_end = """
Вы победили в заказе № {}
Вам начислено {} рублей на баланс
"""

message_lot_deleted = """
Лот удалён
"""

lots_menu_errors = {
    1404: "Лот не найден",
    1300: "Список лотов пустой",
    1330: "Список кандидатов пустой",
    -1: "Вы достигли границы списка"
}
