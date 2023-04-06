message_lot_location_input = """
Введите местоположение
"""

message_lot_task_input = """
Введите описание
"""

message_lot_deadline_input = """
Введите сроки
"""

message_lot_price_input = """
Введите начальную цену
"""

message_lot_file_input = """
Отправьте документ задания
Если хотите добавить несколько документов, добавляйте по одному иначе примется только первый отправленный документ 
"""

message_lot_add_info = """
<b>Локация:</b> {}
<b>Описание:</b> {}
<b>Сроки:</b> {}
<b>Начальная цена:</b> {} рублей
"""

message_lot_send = """
Лот опубликован
"""

message_lot_file_deleted = """
Файлы очищены
"""

message_lot_file_errors = {
    1404: "Вы не добавляли файлы",
    2404: "Принимаются только документы"
}

message_new_lot_notification = """
Уведомление о новом лоте № {}
Местоположение: {}
"""

message_lot_add_error = {
    'value': "Введите целое положительное число больше {}"
}
