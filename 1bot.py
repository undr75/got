import logging
import openai
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Применяем nest_asyncio
nest_asyncio.apply()

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Установите ваш API-ключ OpenAI
openai.api_key = 'sk-LOawRsabmOkBzlpSTeoZPtjM4B6jkI4YzdwyedGuLST3BlbkFJ0S-Di3t73WSbslbas9hM59fQiCTwwcon2wPThr9lkA'

# Создаем словарь для хранения истории сообщений пользователей
user_histories = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Проблема в отношениях", callback_data='relationship')],
        [InlineKeyboardButton("Самооценка и самоценность", callback_data='self-esteem')],
        [InlineKeyboardButton("Тревога и стресс", callback_data='anxiety')],
        [InlineKeyboardButton("Усталость и выгорание", callback_data='burnout')],
        [InlineKeyboardButton("Проблемы на работе", callback_data='work-issues')],
        [InlineKeyboardButton("Другая тема", callback_data='other')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет, я Хэлпи — виртуальный психолог. Я здесь, чтобы помочь вам разобраться с вашими мыслями, "
        "чувствами и ситуациями.\n\n"
        "Помните, что если вы испытываете серьезные расстройства или у вас есть суицидальные мысли, "
        "важно обратиться к специалисту.\n\n"
        "P.S. Я не являюсь заменой живому консультанту и не несу ответственность за ваши действия и решения.\n\n"
        "Моя задача — предложить советы, найти полезные упражнения и техники, помочь вам прояснить ваши ситуации "
        "и поддержать вас на пути к благополучию.\n\n"
        "О чем сегодня хотите поговорить?",
        reply_markup=reply_markup
    )

# Обработка нажатия кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Уведомляем Telegram, что запрос был получен

    # Получаем выбранную тему
    topic = query.data

    # Уведомляем пользователя о выборе темы
    topic_dict = {
        'relationship': "Вы выбрали тему 'Проблема в отношениях'.",
        'self-esteem': "Вы выбрали тему 'Самооценка и самоценность'.",
        'anxiety': "Вы выбрали тему 'Тревога и стресс'.",
        'burnout': "Вы выбрали тему 'Усталость и выгорание'.",
        'work-issues': "Вы выбрали тему 'Проблемы на работе'.",
        'other': "Вы выбрали тему 'Другая тема'."
    }

    await query.edit_message_text(
        text=f"{topic_dict[topic]}\n\nРасскажите подробнее о проблеме, ситуации, ваших чувствах или мыслях:"
    )

    # Инициализируем историю для пользователя, если её нет
    user_id = query.from_user.id
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Сохраняем текущую тему в контексте
    context.user_data['current_topic'] = topic

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text

    # Добавляем сообщение пользователя в историю
    user_histories[user_id].append({"role": "user", "content": user_message})

    try:
        # Отправляем запрос к ChatGPT с историей сообщений и температурой 0.9
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Вы — дружелюбный и эмпатичный виртуальный психолог. "
                                                "Постарайтесь быть поддерживающим и заботливым в своих ответах, "
                                                "и не забудьте задать вспомогательный вопрос в конце некоторых ваших ответов, "
                                                "чтобы помочь пользователю разобраться с его проблемой."}
            ] + user_histories[user_id],  # Используем историю сообщений
            temperature=0.9  # Установка температуры
        )
        bot_message = response['choices'][0]['message']['content']

        # Добавляем ответ бота в историю
        user_histories[user_id].append({"role": "assistant", "content": bot_message})

        # Отправляем ответ пользователю
        await update.message.reply_text(bot_message)

    except Exception as e:
        logger.error(f'Error: {e}')
        await update.message.reply_text('Извините, произошла ошибка при обработке вашего запроса.')

# Обработка ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

async def main():
    # Вставьте свой токен, полученный от BotFather
    token = '7472819901:AAGwi34vKqJgxEVGW1cfVRxoqdb_vgVY88I'

    # Создаем приложение
    application = ApplicationBuilder().token(token).build()

    # На команду /start отвечает функция start
    application.add_handler(CommandHandler("start", start))

    # Обрабатываем нажатия на кнопки
    application.add_handler(CallbackQueryHandler(button))

    # Обрабатываем текстовые сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Логирование ошибок
    application.add_error_handler(error)

    # Запускаем бота
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
