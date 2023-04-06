input_full_name_message = """
Введите своё ФИО, пожалуйста
"""

input_phone_message = """
Введите ваш телефон или нажмите на кнопку ниже
"""

start_message = """
Добро пожаловать!

<b>🛂 ФИО:</b> <code>{}</code>
<b>🆔 ID:</b> <code>{}</code>

<b>{}</b>

<b>💳 Сумма выигранных работ:</b> {} рублей
"""

verification_text = {
    False: "🔴 Верификация не пройдена",
    -1: "🟡 На проверке",
    True: "🟢 Верификация пройдена",
}

username_error = """
Установите ссылку на ваш аккаунт
"""
