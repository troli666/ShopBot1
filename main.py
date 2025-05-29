from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import re

from db import save_appointment #filter

NAME, PHONE, SERVICE, MONTH, DAY, TIME, CONFIRM, CHANGE_FIELD = range(8)

services = ["Манікюр", "Педикюр", "Стрижка", "Макіяж"]
months = ["Травень", "Червень", "Липень"]
days = [str(i) for i in range(1, 32)]
times = [f"{h}:00" for h in range(8, 21, 2)]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я бот бьюті-салону. Як вас звати?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    if context.user_data.get("changing") == "Ім’я":
        return await confirm(update, context)
    await update.message.reply_text("Ваш номер телефону? (10 цифр)")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not re.fullmatch(r"\d{10}", phone):
        await update.message.reply_text("Невірний формат. Введіть 10 цифр:")
        return PHONE
    context.user_data["phone"] = phone
    if context.user_data.get("changing") == "Телефон":
        return await confirm(update, context)
    reply_markup = ReplyKeyboardMarkup([[s] for s in services], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Оберіть послугу:", reply_markup=reply_markup)
    return SERVICE

async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    if context.user_data.get("changing") == "Послуга":
        return await confirm(update, context)
    reply_markup = ReplyKeyboardMarkup([[m] for m in months], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Оберіть місяць:", reply_markup=reply_markup)
    return MONTH

async def get_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["month"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([days[i:i+5] for i in range(0, len(days), 5)], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Оберіть день:", reply_markup=reply_markup)
    return DAY

async def get_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["day"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([times[i:i+3] for i in range(0, len(times), 3)], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Оберіть час:", reply_markup=reply_markup)
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time"] = update.message.text
    if context.user_data.get("changing") == "Дата":
        return await confirm(update, context)
    return await confirm(update, context)

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    context.user_data["changing"] = None  # Скидання
    summary = (
        f"🔍 Перевірте інформацію:\n\n"
        f"👤 Ім’я: {data.get('name')}\n"
        f"📞 Телефон: {data.get('phone')}\n"
        f"💅 Послуга: {data.get('service')}\n"
        f"📅 Дата: {data.get('day')} {data.get('month')} о {data.get('time')}\n\n"
        "Все вірно?"
    )
    markup = ReplyKeyboardMarkup([["Так", "Змінити"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(summary, reply_markup=markup)
    return CONFIRM

async def confirm_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Так":
        save_appointment(context.user_data)  # Збереження заявки в базу даних
        await update.message.reply_text("✅ Заявка збережена!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        options = [["Ім’я", "Телефон"], ["Послуга", "Дата"]]
        markup = ReplyKeyboardMarkup(options, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Що хочете змінити?", reply_markup=markup)
        return CHANGE_FIELD


async def change_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field = update.message.text
    context.user_data["changing"] = field

    if field == "Ім’я":
        await update.message.reply_text("Введіть нове ім’я:", reply_markup=ReplyKeyboardRemove())
        return NAME
    elif field == "Телефон":
        await update.message.reply_text("Введіть новий номер телефону:", reply_markup=ReplyKeyboardRemove())
        return PHONE
    elif field == "Послуга":
        reply_markup = ReplyKeyboardMarkup([[s] for s in services], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Оберіть нову послугу:", reply_markup=reply_markup)
        return SERVICE
    elif field == "Дата":
        reply_markup = ReplyKeyboardMarkup([[m] for m in months], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Оберіть новий місяць:", reply_markup=reply_markup)
        return MONTH

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Запис скасовано. Якщо передумаєте – /start", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token("7681600164:AAF4RU_nMm3dAf2EMp5q08f3boNj6WYJ46o").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)],
            MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_month)],
            DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_day)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_choice)],
            CHANGE_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_field)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Бот запущено...")
    app.run_polling()

if __name__ == "__main__":
    main()
