from flask import Flask, render_template
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_appointments():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()
    cur.execute("SELECT name, phone, service, month, day, time FROM appointments ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route("/")
def admin_panel():
    data = get_appointments()
    return render_template("admin.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
