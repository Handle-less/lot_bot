message_report_select = """
Выберите вопрос
"""

message_report_info = """
Вопрос от @{} | отправлен {}
{}
"""

message_report_answer_input = """
Введите ответ
"""

message_report_answer_admin = {
    1: "Ответ отправлен",
    0: "Отклонение отправлено"
}

message_report_answer_for_user = {
    1: "❗ Был получен ответ на ваш вопрос от {}\n"
       "<b>{}</b>",
    0: "❗ Ваш вопрос от {} был отклонен!"
}

message_report_errors = {
    1404: "Вопрос не найден",
    1300: "Вы достигли границы списка",
    1000: "Список вопросов пустой"
}
