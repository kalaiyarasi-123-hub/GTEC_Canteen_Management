from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
        if password == "admin123":
            return redirect(url_for("manager"))
        else:
            error = "Wrong Password ❌"

    return render_template("manager_login.html", error=error)

# MANAGER PAGE
@app.route("/manager")
def manager():
    return render_template("manager.html")
# ORDERS
@app.route("/orders")
def orders():
    return render_template("orders.html")

if __name__ == "__main__":
    app.run()
