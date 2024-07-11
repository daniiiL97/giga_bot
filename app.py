import time
import telebot
from telebot import types
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

KEY = ('7232254506:AAEzof7JkzS_xmjgoAMCfQe-5kGoANtjkVg')
bot = telebot.TeleBot(KEY)

# Initialize GigaChat
chat = GigaChat(credentials="MGQ3ODgzNGQtMTAyYS00MjA0LTg0MmMtMjJjMTEwNGZmOGQ4OmZjNzAzODI4LTYxYWMtNDIxMC05MTU0LThkMGZlMDA4N2RmMA==", verify_ssl_certs=False)

user_summary_length = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Начать", callback_data="start_button"))
    bot.send_message(message.chat.id, "Добро пожаловать в бота для суммаризации текста! 📚✨\n"
                                      "Этот бот использует модель GigaChat для создания кратких суммаризаций текстов на русском языке.",
                                      reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_button")
def next(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Далее", callback_data="next"))
    bot.send_message(call.message.chat.id,
                     "Как использовать бота:\n"
                     "1. Начало работы: Нажмите кнопку 'Начать' ниже. ▶️\n"
                     "2. Выбор длины суммаризации: После нажатия кнопки 'Начать' выберите длину суммаризации:\n"
                     "   - Краткая: Для самых кратких обзоров (примерно 20 слов). ✨\n"
                     "   - Средняя: Для более детализированных суммаризаций (примерно 50 слов). 🌟\n"
                     "   - Подробная: Для максимально подробных суммаризаций (примерно 100 слов). 🌠\n"
                     "3. Ввод текста: После выбора длины суммаризации введите текст, который хотите суммировать. 🖊️\n"
                     "4. Получение результата: Подождите, пока бот обработает ваш текст и создаст суммаризацию. ⏳\n\n"
                     "Примечание: Убедитесь, что ваш текст содержит не более 600 слов для корректной работы модели. ⚠️\n\n"
                     "Начните с нажатия кнопки 'Далее' и следуйте инструкциям. Приятного использования! 🎉",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "next")
def start_summary_process(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Краткая")
    btn2 = types.KeyboardButton("Средняя")
    btn3 = types.KeyboardButton("Подробная")
    markup.add(btn1, btn2, btn3)
    bot.send_message(call.message.chat.id, 'Привет! Выбери размер суммаризации: Краткая, Средняя или Подробная.',
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Краткая", "Средняя", "Подробная"])
def set_summary_length(message):
    if message.text == "Краткая":
        user_summary_length[message.chat.id] = 20
    elif message.text == "Средняя":
        user_summary_length[message.chat.id] = 50
    elif message.text == "Подробная":
        user_summary_length[message.chat.id] = 100
    bot.send_message(message.chat.id,
                     f'Выбран размер суммаризации: {message.text}. Теперь введи текст для суммаризации.',
                     reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(content_types=['text'])
def answer(message):
    if message.chat.id not in user_summary_length:
        bot.send_message(message.chat.id,
                         'Пожалуйста, сначала выбери размер суммаризации, используя команды: Краткая, Средняя или Подробная.')
        return

    bot.send_message(message.chat.id, 'Анализируем текст...')
    article_text = message.text
    summary_length = user_summary_length[message.chat.id]

    def generate_summary():
        nonlocal article_text, summary_length, message
        progress_message = bot.send_message(message.chat.id, 'Генерация суммаризации...')
        for i in range(10):
            time.sleep(1)
            bot.edit_message_text(chat_id=message.chat.id, message_id=progress_message.message_id,
                                  text=f'Генерация суммаризации... {i * 10}%')

        messages = [
            SystemMessage(
                content=f"Ты суммаризируешь текст максимально точно на русском. Количество слов на выходе должно быть ровно {summary_length}. Если это невозможно, сократи текст до максимально близкого к указанному числу слов."
            ),
            HumanMessage(content=article_text),
        ]

        response = chat.invoke(messages)
        summary = response.content

        bot.send_message(message.chat.id, summary)
        do_again(message)

    threading.Thread(target=generate_summary).start()

def do_again(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Краткая")
    btn2 = types.KeyboardButton("Средняя")
    btn3 = types.KeyboardButton("Подробная")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     'Хочешь проверить другой текст? Выбери размер суммаризации: Краткая, Средняя или Подробная.',
                     reply_markup=markup)

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
