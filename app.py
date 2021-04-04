from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send, join_room, leave_room
import random
import string
from user import Users, PROFILE_TRAITS
from room import Rooms

app = Flask(__name__)
app.secret_key = bytes("".join(random.choice(string.printable) for _ in range(20)), "utf-8")
socketio = SocketIO(app, logger=True)
users = Users()
rooms = Rooms()

random_prompts = [
    "Do you love working from home or would you rather be in the office? Is there a balance of both that you like best?",
    "What’s the hardest part about working virtually for you? The easiest?",
    "Do you have a dedicated office space at home?",
    "Show us your office space!",
    "Where do you work most frequently from at home? Your office? Your kitchen table? The backyard? Your bed?",
    "Be honest, how often do you work from bed?",
    "What did you eat for breakfast?",
    "What does your morning routine look like when working from home?",
    "What’s your number one tip for combating distractions when working from home?",
    "How do you stay productive and motivated working virtually?",
    "What does your typical work from home uniform look like?",
    "How many cups of coffee, tea, or beverage-of-choice do you have each morning?",
    "Are you an early bird or night owl?",
    "What about showers? Do you prefer morning or night?",
    "What’s one thing we could do to improve our virtual meetings?",
    "What’s your favorite flower or plant?",
    "What’s your caffeinated beverage of choice? Coffee? Cola? Tea?",
    "What’s your favorite scent?",
    "What’s the last great TV show or movie you wanted?",
    "Best book you’ve ever read?",
    "Best professional development book you’ve ever read?",
    "If you could learn one new professional skill, what would it be?",
    "If you could learn one new personal skill, what would it be?",
    "What’s your favorite way to get in some exercise?",
    "If you could write a book, what genre would you write it in? Mystery? Thriller? Romance? Historical fiction? Non-fiction?",
]

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
        roomname = username
        rooms.add(roomname, [user])
    else:
        max_per_group = int(request.form.get("max_per_group") or 4)
        pickable_rooms = list(filter(lambda room: len(room.users) < max_per_group, rooms.rooms.values()))
        roomname = max(pickable_rooms, key=lambda x: x.score(profile)).roomname
        if user not in rooms[roomname].users:
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
    msg = "%s entered the room. Ice-breaker question: %s" % (username, random.choice(random_prompts))
    print(msg)
    rooms[roomname].messages.append(msg)
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
    rooms[roomname].messages.append(msg)
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
