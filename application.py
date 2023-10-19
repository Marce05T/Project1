import os
import requests
from flask import Flask, session, render_template, request, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

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

api_key = "AIzaSyBR0bjH_FYgC5C2OeaCtmtIBKOlYYgrmF8"
base_url = "https://www.googleapis.com/books/v1/volumes"


@app.route("/", methods=["GET","POST"])
def index():
    resultados =[]
    
    if session.get("user_id") is None:
            return redirect("/login")
        
    if request.method == "POST":
        index_r = request.form.get("index")
        
        resultados = db.execute(text("SELECT numisbn FROM books WHERE title LIKE :index_r OR author LIKE :index_r OR numisbn LIKE :index_r"), {"index_r": f"%{index_r}%"}).fetchall()
        
    img_urls = []
    titulos = []
        
    for resultado in resultados:
        response = requests.get(f"{base_url}?q=isbn:{resultado['numisbn']}&key={api_key}").json()
        img_smalltmbnl = response['items'][0]['volumeInfo']['imageLinks']['smallThumbnail']
        title = response['items'][0]['volumeInfo']['title']
        
        img_urls.append(img_smalltmbnl)  # Agrega la URL de la imagen en miniatura a la lista
        titulos.append(title)

    return render_template("index.html", resultados=resultados, img_urls = img_urls, titulos = titulos)


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        usuario_existente= db.execute(text("SELECT id FROM lectores WHERE name = :name"), {"name": name}).fetchone()
        
        if usuario_existente:
            flash("Este nombre ya esta en uso")
            return render_template("register.html")
        if len(password) < 8 or len(password) > 20:
            flash("Contraseña invalida")
            return render_template("register.html") 
        if password != confirmation:
            flash("Las contraseñas no coinciden")
            return render_template("register.html")
        else:
            password = generate_password_hash(password)
            
            result = db.execute(text("INSERT INTO lectores (name, password) VALUES (:name, :password)"), {"name": name, "password": password})

            result = db.execute(text("SELECT lastval()"))
            user_id = result.scalar()
            
            session["user_id"] = user_id
            return redirect("/")
        
    else:
        return render_template("register.html")
            
    
@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        query = text("SELECT * FROM lectores WHERE name = :username")
        result = db.execute(query, {"username": username}).fetchone()

        if result is None or not check_password_hash(result["password"], password):
            flash("Usuario y/o contraseña incorrecto")
            return render_template("login.html")
        else:
            session["user_id"] = result["id"]
            return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


   