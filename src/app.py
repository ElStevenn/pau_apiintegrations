from quart import Quart, render_template, request, jsonify, redirect, url_for, session
from werkzeug.exceptions import HTTPException
from uuid import UUID

from app.database.crud.base_user import UserService

version = "Alpha 0.1.1"
app = Quart(__name__)
app.secret_key = "paus_secret_key"


async def register_user(username: str, email: str, password: str):
    return await UserService.create({"username": username,
                                     "email":    email,
                                     "password": password})

@app.route("/")
async def index():
    raw_id = session.get("user_id")
    user = None

    if raw_id:
        try:
            user_uuid = UUID(raw_id)
            user = await UserService.get(str(user_uuid))
        except (ValueError, HTTPException):
            session.pop("user_id", None)

    return await render_template("landing_page.html", user=user, version=version)

@app.route("/register", methods=["GET", "POST"])
async def register():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "GET":
        return await render_template("login_register.html", active="register", error=None)

    data = (await request.get_json()) or (await request.form)
    username = data.get("regName")
    email = data.get("regEmail")
    password = data.get("regPassword")

    if not all([username, email, password]):
        return jsonify({"error": "regName, regEmail and regPassword are required"}), 400

    try:
        result = await UserService.create({"username": username, "email": email, "password": password})
    except HTTPException as e:
        return jsonify({"error": e.description}), e.code

    session["user_id"] = result["id"]
    return jsonify(result), 200

@app.route("/login", methods=["GET", "POST"])
async def login(): 
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "GET":
        return await render_template("login_register.html", active="login", error=None)

    data = (await request.get_json()) or (await request.form)
    email = data.get("loginEmail")
    password = data.get("loginPassword")

    try:
        result = await UserService.authenticate(email, password)
    except HTTPException as e:
        if request.is_json:
            return jsonify({"error": e.description}), e.code
        return await render_template("login_register.html", active="login", error=e.description), e.code

    session["user_id"] = result["id"]

    if request.is_json:
        return jsonify({"user_id": result["id"]}), 200

    return redirect(url_for("plataform"), code=303) 

@app.route("/logout")
async def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))

@app.route("/plataform")
async def plataform():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    try:
        user = await UserService.get(user_id)
    except HTTPException:
        session.pop("user_id", None)
        return redirect(url_for("login"))

    return await render_template("main_panel.html", user=user)

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
