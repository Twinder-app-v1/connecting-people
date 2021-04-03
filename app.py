from flask import Flask, render_template, request, redirect, session
import user

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
users = user.UserModel()

@app.route("/")
def home_page():
    if "username" in session:
        username = session["username"]
        return render_template("home_page.html", username=username)
    else:
        return render_template("landing_page.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        if "username" in session:
            return redirect("/")
        else:
            return render_template("login_page.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username].validate(password):
            session["username"] = username
            return redirect("/")
        else:
            err = "Invalid login credentials"
            return render_template("login_page.html", err=err)

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        if "username" in session:
            return redirect("/")
        else:
            return render_template("register_page.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            err = "Username taken"
            return render_template("register_page.html", err=err)
        else:
            users.add(username, password)
            session["username"] = username
            return redirect("/")

@app.route("/logout")
def logout_page():
    session.pop("username", None)
    return redirect("/")

@app.route("/profile")
def profile_page():
    if "username" in session:
        return render_template("profile_page.html")
    else:
        return redirect("/")

@app.route("/chat")
def chat_list_page():
    if "username" in session:
        return render_template("chat_list_page.html")
    else:
        return redirect("/")

@app.route("/chat/<string:chat_id>")
def chat_page(chat_id):
    if "username" in session:
        return render_template("chat_page.html", chat_id=chat_id)
    else:
        return redirect("/")
