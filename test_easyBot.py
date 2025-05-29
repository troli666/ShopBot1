from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import psycopg2
import asyncio

# Параметри підключення до БД — зміни під свої
DB_NAME="beauty_salon"
DB_USER="postgres"
DB_PASS="soso4ek69"
DB_HOST="localhost"
DB_PORT="5432"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Бот працює!')

# Функція для отримання даних з БД (під капотом синхронна, тому запускаємо в пулі)
def get_appointments():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM appointments;")
        rows = cur.fetchall()
    conn.close()
    return rows

async def show_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loop = asyncio.get_running_loop()
    rows = await loop.run_in_executor(None, get_appointments)
    if not rows:
        await update.message.reply_text("Таблиця appointments порожня.")
        return

    text = "Записи в таблиці appointments:\n"
    for row in rows:
        text += str(row) + "\n"
    # Якщо повідомлення занадто довге, можна подумати про розбиття на частини
    await update.message.reply_text(text)

def main():
    application = Application.builder().token("7681600164:AAF4RU_nMm3dAf2EMp5q08f3boNj6WYJ46o").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("show", show_appointments))  # додаємо команду /show
    application.run_polling()

if __name__ == "__main__":
    main()
