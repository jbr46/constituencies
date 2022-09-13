import os
import requests
import urllib.parse
import random

from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL
from datetime import datetime

db = SQL("sqlite:///constituencies.db")


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def generate_constituency():
    constituency = db.execute("SELECT MP, party, constituency FROM constituencies WHERE id = ?", random.randint(0, 648))[0]
    return constituency

def get_personal_bests(id):
    bests = db.execute("SELECT score, date FROM bests WHERE id = ? ORDER BY score DESC LIMIT 5", id)
    return bests

def add_bests(score, username, id, bests):
    now = datetime.now()
    try:
        if score > bests[4]["score"]:
            db.execute("INSERT INTO bests (score, date, username, id) VALUES (?, ?, ?, ?)", score, now.strftime("%d/%m/%Y"), username, id)
    except IndexError:
            db.execute("INSERT INTO bests (score, date, username, id) VALUES (?, ?, ?, ?)", score, now.strftime("%d/%m/%Y"), username, id)
    return

def get_bests():
    bests = db.execute("SELECT score, username, date FROM bests ORDER BY score DESC LIMIT 5")
    return bests

