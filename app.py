from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import date

app = Flask(__name__)

# ---------------- DATABASE ---------------- #

def get_db():
    conn = sqlite3.connect("canteen.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            items TEXT,
            total INTEGER,
            status TEXT,
            order_date TEXT
        )
    """)
    db.commit()

init_db()

# ---------------- PAGES ---------------- #

# HOME PAGE
@app.route("/")
def index():
    return render_template("index.html")

# STUDENT PAGE
@app.route("/student")
def student():
    return render_template("student.html")

# MANAGER LOGIN PAGE
@app.route("/manager_login", methods=["GET", "POST"])
def manager_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")

        # ✅ Manager Password
        if password == "gtec12345":
            return redirect(url_for("manager"))
        else:
            error = "Wrong Password ❌"

    return render_template("manager_login.html", error=error)

# MANAGER PAGE
@app.route("/manager")
def manager():
    return render_template("manager.html")

# ORDERS PAGE
@app.route("/orders")
def orders():
    return render_template("orders.html")

# ---------------- API ---------------- #

# PLACE ORDER (Student side)
@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.json

    order_id = data.get("orderId")
    items = str(data.get("items"))
    total = data.get("total")
    today = date.today().strftime("%d-%m-%Y")

    db = get_db()
    c = db.cursor()
    c.execute("""
        INSERT INTO orders (order_id, items, total, status, order_date)
        VALUES (?, ?, ?, ?, ?)
    """, (order_id, items, total, "Pending", today))

    db.commit()
    return jsonify({"success": True})

# GET ALL ORDERS (Manager side)
@app.route("/get_orders")
def get_orders():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = c.fetchall()

    orders = []
    for r in rows:
        orders.append({
            "orderId": r["order_id"],
            "items": r["items"],
            "total": r["total"],
            "status": r["status"],
            "date": r["order_date"]
        })

    return jsonify(orders)

# UPDATE STATUS
@app.route("/update_status", methods=["POST"])
def update_status():
    data = request.json
    order_id = data.get("orderId")
    status = data.get("status")

    db = get_db()
    c = db.cursor()
    c.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
    db.commit()

    return jsonify({"success": True})

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
