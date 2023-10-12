import os

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.hmtl")

@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()

    if request.method == "POST":

        profesion = int(request.form.get("profesion"))

        if profesion == 1:

            rows = db.execute("SELECT * FROM profesores WHERE name = ?", request.form.get("username"))

            if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
                flash("Usuario incorrecto y/o contraseña")
                return render_template("login.html")
            else:
                session["user_id"] = rows[0]["id"]
                session["profesor"] = True
                return redirect("/")

        elif profesion == 2:
            rows = db.execute("SELECT * FROM estudiantes WHERE name = ?", request.form.get("username"))

            if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
                flash("Usuario incorrecto y/o contraseña")
                return render_template("login.html")
            else:
                session["user_id"] = rows[0]["id"]
                return redirect("/")


    else:
        return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        user = db.execute("SELECT id FROM lectores WHERE name = ?",name)

        users = []
        for i in user:
            users.append(i)
        if len(users) != 0:
            error = "Este nombre ya existe"
            return render_template("register_stu.html", error = error)
        if password != confirmation:
            error = "La contraseña no coincide"
            return render_template("register_stu.html", error = error)
        else:
            password = generate_password_hash(password)
            user = db.execute("INSERT INTO estudiantes(name,password) VALUES(?,?)",name,password)
            session["id"] = users
            return redirect("/")
    else:
        return render_template("register.html")