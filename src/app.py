# app.py
from quart import Quart, render_template, request, jsonify, redirect, url_for, session
import asyncio
from app.database.crud import register_user as _reg_sync, \
                                 login_user    as _login_sync, \
                                 get_user      as _get_sync

version = "0.1.1"

async def register_user(username: str, email: str, password: str):
    return await asyncio.to_thread(_reg_sync, username, email, password)

async def login_user(username: str, password: str):
    return await asyncio.to_thread(_login_sync, username, password)

async def get_user(user_id: int):
    return await asyncio.to_thread(_get_sync, user_id)

app = Quart(__name__)
app.secret_key = "paus_secret_key"

@app.route("/")
async def index():
    user = None
    if session.get("user_id"):
        user = await get_user(session["user_id"])
    return await render_template("landing_page.html", user=user, version=version)

@app.route("/login", methods=["GET", "POST"])
async def login():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "GET":
        return await render_template("login_register.html",
                                     active="login",
                                     user=None,
                                     )

    data = await request.get_json() or await request.form
    result = await login_user(
        username=data.get("loginEmail"),
        password=data.get("loginPassword")
    )
    if result.get("user_id"):
        session["user_id"] = result["user_id"]
        return jsonify(result), 200

    return jsonify({"error": result.get("error", "Login failed")}), 401

@app.route("/register", methods=["GET", "POST"])
async def register():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "GET":
        return await render_template("login_register.html",
                                     active="register",
                                     user=None)

    data = await request.get_json() or await request.form
    result = await register_user(
        username=data.get("regName"),
        email=data.get("regEmail"),
        password=data.get("regPassword")
    )
    if result.get("user_id"):
        session["user_id"] = result["user_id"]
        return jsonify(result), 200

    return jsonify({"error": result.get("error", "Registration failed")}), 400

@app.route("/logout")
async def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))

@app.route("/plataform")
async def plataform():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = await get_user(session["user_id"])
    return await render_template("main_panel.html", user=user)

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
