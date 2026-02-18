from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import json
from datetime import date

# ---------------- APP CONFIG ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "canteen.db")

app = Flask(__name__)

# ---------------- DATABASE ---------------- #

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            items TEXT,
            total INTEGER,
            status TEXT,
            order_date TEXT
        )
    """)
    db.commit()
    db.close()

init_db()

# ---------------- PAGES ---------------- #

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/student")
def student():
    return render_template("student.html")

@app.route("/manager_login", methods=["GET", "POST"])
def manager_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")

        if password == "gtec12345":
            return redirect(url_for("manager"))
        else:
            error = "Wrong Password ❌"

    return render_template("manager_login.html", error=error)

@app.route("/manager")
def manager():
    return render_template("manager.html")

@app.route("/orders")
def orders_page():
    return render_template("orders.html")

# ---------------- API ---------------- #

@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.get_json()

    if not data:
        return jsonify({"success": False})

    today = date.today().strftime("%d-%m-%Y")

    db = get_db()
    c = db.cursor()

    # Count today's orders
    c.execute("SELECT COUNT(*) FROM orders WHERE order_date=?", (today,))
    count = c.fetchone()[0]

    serial_no = str(count + 1).zfill(3)
    order_id = f"{today}-{serial_no}"

    items = json.dumps(data.get("items", []))
    total = data.get("total", 0)

    c.execute("""
        INSERT INTO orders (order_id, items, total, status, order_date)
        VALUES (?, ?, ?, ?, ?)
    """, (order_id, items, total, "Pending", today))

    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "orderId": order_id
    })

@app.route("/get_orders")
def get_orders():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = c.fetchall()
    db.close()

    orders = []
    for r in rows:
        try:
            items = json.loads(r["items"]) if r["items"] else []
        except:
            items = []

        orders.append({
            "orderId": r["order_id"],
            "items": items,
            "total": r["total"],
            "status": r["status"],
            "date": r["order_date"]
        })

    return jsonify(orders)

@app.route("/update_status", methods=["POST"])
def update_status():
    data = request.get_json()
    order_id = data.get("orderId")
    status = data.get("status")

    db = get_db()
    c = db.cursor()
    c.execute(
        "UPDATE orders SET status=? WHERE order_id=?",
        (status, order_id)
    )
    db.commit()
    db.close()

    return jsonify({"success": True})


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
