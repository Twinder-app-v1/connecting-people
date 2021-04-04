from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send, join_room, leave_room
import user
import room
import random
import numpy as np

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socketio = SocketIO(app)
users = user.Users()
rooms = room.Rooms()

random_roomnames = ["blue", "red", "green", "purple", "orange", "pink", "yellow", "green"]

@app.route("/")
def home_page():
    if "username" in session:
        username = session["username"]
        profile = users[username].profile
        return render_template("home_page.html", username=username, profile=profile)
    else:
        return render_template("landing_page.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if "username" in session:
        return redirect("/")
    if request.method == "GET":
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

def user_join_room(username, roomname):
    user = users[username]
    if roomname not in rooms:
        rooms.add(roomname, [user])
    else:
        rooms[roomname].users.append(user)
    print("%s joined room %s" % (username, roomname))
    return redirect("/chat/" + roomname)

@app.route("/profile", methods=["POST"])
def join_profile_room():
    if "username" not in session:
        return redirect("/")
    profile = [
        int(request.form.get("sloppy-neat") or 0),
        int(request.form.get("shy-outgoing") or 0),
        int(request.form.get("lazy-active") or 0),
        int(request.form.get("serious-playful") or 0),
        int(request.form.get("grouchy-nice") or 0),
        int(request.form.get("evil-good") or 0),
    ]
    username = session["username"]
    users[username].profile = profile
    users.save()
    if len(rooms) == 0:
        err = "No rooms available"
        return render_template("home_page.html", err=err, profile=profile)
    roomname = rooms.closests_profile_match(profile).roomname
    return user_join_room(username, roomname)

@app.route("/random_create")
def create_random_room():
    if "username" not in session:
        return redirect("/")
    username = session["username"]
    roomname = random.choice(random_roomnames)
    return user_join_room(username, roomname)

@app.route("/random_join")
def join_random_room():
    if "username" not in session:
        return redirect("/")
    username = session["username"]
    if len(rooms) == 0:
        err = "No rooms available"
        profile = users[username].profile
        return render_template("home_page.html", err=err, profile=profile)
    else:
        roomname = random.choice(list(filter(
            lambda x: x not in rooms.has_user(username), rooms.rooms.keys()
        )))
    return user_join_room(username, roomname)

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

@socketio.on("disconnect")
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
    print(rooms[roomname].combined_users_profile())
    send(msg, room=roomname)
