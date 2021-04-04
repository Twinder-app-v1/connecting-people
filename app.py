from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send, join_room, leave_room
import random
import string
from user import Users, PROFILE_TRAITS
from room import Rooms

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.secret_key = bytes("".join(random.choice(string.printable) for _ in range(20)), "utf-8")
socketio = SocketIO(app, logger=True)
users = Users()
rooms = Rooms()

# Think of a better design than this ...
random_roomnames = ["blue", "red", "green", "purple", "orange", "pink", "yellow", "green"]

@app.route("/")
def home_page(err=""):
    if "username" in session:
        username = session["username"]
        profile = users[username].profile
        return render_template("home_page.html", username=username, profile=profile, err=err)
    else:
        return render_template("landing_page.html")

@app.route("/login", methods=["GET", "POST"])
def login_page(err=""):
    if "username" in session:
        return redirect("/")
    if request.method == "GET":
        return render_template("login_page.html", err=err)
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
    if "username" in session:
        return redirect("/")
    if request.method == "GET":
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

@app.route("/profile", methods=["POST"])
def join_room_post():
    if "username" not in session:
        return redirect("/")

    # Save information
    profile = list(map(
        lambda trait: (trait, bool(request.form.get("trait-"+trait))),
        PROFILE_TRAITS))
    username = session["username"]
    users[username].profile = profile
    users.save()

    # Join room
    user = users[username]
    if len(rooms) == 0:
        roomname = "room-one"
        rooms.add(roomname, [user])
    else:
        roomname = max(rooms.rooms.values(), key=lambda x: x.score(profile)).roomname
        rooms[roomname].add(user)

    print("%s joined room %s" % (username, roomname))
    return redirect("/chat/" + roomname)

@app.route("/chat")
def chat_list_page():
    if "username" not in session:
        return redirect("/")
    username = session["username"]
    rs = rooms.has_user(username)
    return render_template("chat_list_page.html", rooms=rs)

@app.route("/chat/<string:roomname>")
def chat_page(roomname):
    if "username" not in session:
        return redirect("/")
    if roomname not in rooms:
        return redirect("/chat")
    username = session["username"]
    if username not in map(lambda u: u.username, rooms[roomname].users):
        return redirect("/chat")
    session["roomname"] = roomname
    room = rooms[roomname]
    return render_template("chat_page.html", room=room)

@socketio.on("connect")
def on_connect():
    if "username" not in session or "roomname" not in session:
        return
    username = session["username"]
    roomname = session["roomname"]
    if roomname not in rooms:
        return
    join_room(roomname)
    for msg in rooms[roomname].messages:
        send(msg)
    msg = "%s entered the room" % username
    print(msg)
    send(msg, room=roomname)

@socketio.on("leave")
def on_disconnect():
    if "username" not in session or "roomname" not in session:
        return
    username = session["username"]
    roomname = session["roomname"]
    if roomname not in rooms:
        return
    leave_room(roomname)
    msg = "%s left the room" % username
    print(msg)
    send(msg, room=roomname)

@socketio.on("message")
def on_message(data):
    if "username" not in session or "roomname" not in session:
        return
    username = session["username"]
    roomname = session["roomname"]
    if roomname not in rooms:
        return
    print("%s@%s: %s" % (username, roomname, data))
    msg = "%s: %s" % (username, data)
    rooms[roomname].messages.append(msg)
    send(msg, room=roomname)
