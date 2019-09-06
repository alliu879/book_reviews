import os
import requests

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""
    if request.method == "POST":
        option = request.form.get("option")
        search = request.form.get("search")
        if request.form.get("option") == "isbn":
            results = db.execute("SElECT * FROM books WHERE isbn LIKE :isbn", {"isbn": '%' + search + '%'}).fetchall()
        if request.form.get("option") == "title":
            results = db.execute("SElECT * FROM books WHERE title LIKE :title", {"title": '%' + search + '%'}).fetchall()
        if request.form.get("option") == "author":
            results = db.execute("SElECT * FROM books WHERE author LIKE :author", {"author": '%' + search + '%'}).fetchall()
        # results = db.execute("SELECT * FROM books WHERE :option = :search", {"option": option, "search": search}).fetchall()
        return render_template("results.html", results=results)
    else:
        return render_template("index.html")

@app.route("/books/<int:id>", methods=["GET", "POST"])
def book(id):
    """Lists details about a single book."""

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": id}).fetchone()
    # Make sure book exists.
    if book is None:
        return apology("Book does not exist.")

    if request.method == "POST":
        review = request.form.get("review")
        rating = request.form.get("rating")
        prevReviews = db.execute("SELECT * FROM reviews WHERE userid = :userid AND bookid = :bookid", {"userid": session['user_id'], "bookid": book.id}).fetchall()
        if not prevReviews:
            db.execute("INSERT INTO reviews (bookid, content, rating, userid) VALUES (:bookid, :content, :rating, :userid)", {"bookid": book.id, "content": review, "rating": rating, "userid": session['user_id']})
            db.commit()
        else:
            return apology("You can only submit one review")

    reviews = db.execute("SELECT bookid, content, rating, username FROM reviews JOIN users ON reviews.userid = users.id WHERE bookid = :bookid", {"bookid": id}).fetchall()

    return render_template("book.html", book=book, id=id, reviews=reviews)


@app.route("/api/books/<string:isbn>")
def book_api(isbn):
    """Return details about a single flight."""

    # Make sure flight exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 404

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "sFxB13KnCOXBIqx0DiNWyQ", "isbns": book.isbn})
    print(res.json())
    return render_template("book_api.html", json=res.json())


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Missing username")
        elif not request.form.get("password"):
            return apology("Missing password")
        elif not request.form.get("confirmation"):
            return apology("Must confirm password")
        # Personal touch:
        elif len(request.form.get("password")) < 7:
            return apology("Password must be at least seven characters")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match")

        result = db.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchone()
        if result:
            return apology("Username already in database")
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", {"username": request.form.get("username"), "hash": generate_password_hash(request.form.get("password"))})
        db.commit()

        session["user_id"] = result

        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
        print("33333333")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
