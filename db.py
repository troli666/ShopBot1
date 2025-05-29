import psycopg2
from dotenv import load_dotenv
import os

# Завантаження змінних середовища з .env
load_dotenv()

# Параметри підключення з .env
conn = psycopg2.connect(
    dbname="beauty_salon",
    user="salon_user",
    password="my_secure_password",
    host="localhost",
    port="5432"
)

# Функція збереження заявки
def save_appointment(data):
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO appointments (name, phone, service, month, day, time)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    data["name"],
                    data["phone"],
                    data["service"],
                    data["month"],
                    data["day"],
                    data["time"]
                )
            )