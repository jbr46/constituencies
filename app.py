import os
import datetime
import pymysql.cursors


from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, generate_constituency, add_bests, get_bests, get_personal_bests

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

connection = pymysql.connect(unix_socket='/cloudsql/adept-lodge-362420:us-central1:constituencies',
                             user='jbr46',
                             password='constituencies',
                             database='constituencies',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def play():
    """Play game"""
    if request.method == "POST":
        answer = request.form.get("answer")
        score = int(request.form.get("score"))
        constituency = request.form.get("constituency")
        name = request.form.get("name")
        if answer.casefold() == constituency.casefold():
            score += 1
            new_constituency = generate_constituency()
            return render_template("game.html", constituency=new_constituency, score=score)
        else:
            if session.get("user_id") is None:
                add_bests(score, "Guest", -1, get_bests())
            else:
                with connection:
                    with connection.cursor() as cursor:
                        sql = "SELECT `username` FROM `users` WHERE `id` = %i"
                        cursor.execute(sql, (session["user_id"],))
                        username = cursor.fetchone()
                add_bests(score, username, session["user_id"], get_personal_bests(session["user_id"]))
            connection.close()
            return render_template("game_over.html", score=score, name=name, answer=answer)

    else:
        constituency = generate_constituency()
        score = 0
        return render_template("game.html", constituency=constituency, score=score)

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
        with connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `users` WHERE `username` = %s"
                cursor.execute(sql, (request.form.get("username"),))
                rows = cursor.fetchone()
        connection.close()

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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        with connection:

            username = request.form.get("username")
            password = request.form.get("password")

            # Ensure username was submitted
            if not username:
                connection.close()
                return apology("must provide username", 400)

            # Ensure username not already taken
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(id) FROM `users` WHERE `username` = %s"
                cursor.execute(sql, (username),)
                check = cursor.fetchone()["COUNT(id)"]

            #check = db.execute("SELECT COUNT(id) FROM users WHERE username = ?", username)[0]["COUNT(id)"]
            if check:
                connection.close()
                return apology("username already taken", 400)

            # Ensure password was submitted
            if not password or not request.form.get("confirmation"):
                connection.close()
                return apology("must provide password", 400)

            # Check passwords match
            if password != request.form.get("confirmation"):
                connection.close()
                return apology("passwords do not match", 400)

                
            with connection.cursor() as cursor:
                sql = "INSERT INTO `users` (`username`, `hash`) VALUES (%s, %s)"
                cursor.execute(sql, (username, generate_password_hash(password),))
            connection.commit()

            #db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
            connection.close()
            return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/bests")
@login_required
def personal_bests():
    bests = get_personal_bests(session["user_id"])
    return render_template("bests.html", bests=bests)

@app.route("/bests_all")
def bests():
    bests = get_bests()
    return render_template("bests_all.html", bests=bests)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


