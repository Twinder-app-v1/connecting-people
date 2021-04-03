from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template("home_page.html", data=9)

@app.route("/login")
def login_page():
    return render_template("login_page.html", data=9)

@app.route("/profile")
def profile_page():
    return render_template("profile_page.html", data=9)

@app.route("/chat")
def chat_list_page():
    return render_template("chat_list_page.html", data=9)

@app.route("/chat/<string:chat_id>")
def chat_page_page():
    return render_template("chat_page_page.html", data=9)
