import os
import requests
import urllib.parse
import random
import pymysql.cursors

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime

connection = pymysql.connect(unix_socket='/cloudsql/adept-lodge-362420:us-central1:constituencies',
                             user='jbr46',
                             password='constituencies',
                             database='constituencies',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)


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
  with connection.cursor() as cursor:
    sql = "SELECT `MP`, `party`, `constituency` FROM `constituencies` WHERE `id` = %s"
    cursor.execute(sql, (random.randint(0, 648),))
    constituency = cursor.fetchone()

    #constituency = db.execute("SELECT MP, party, constituency FROM constituencies WHERE id = ?", random.randint(0, 648))[0]
    return constituency

def get_personal_bests(id):
    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT `score`, `date` FROM `bests` WHERE `id` = %s ORDER BY `score` DESC LIMIT 5"
            cursor.execute(sql, (id,))
            bests = cursor.fetchone()

    #bests = db.execute("SELECT score, date FROM bests WHERE id = ? ORDER BY score DESC LIMIT 5", id)
    connection.close()
    return bests

def add_bests(score, username, id, bests):
    with connection:
        now = datetime.now()
        try:
            if score > bests[4]["score"]:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO `bests` (`score`, `date`, `username`, `id`) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (score, now.strftime("%d/%m/%Y"), username, id,))
                connection.commit()

                #db.execute("INSERT INTO bests (score, date, username, id) VALUES (?, ?, ?, ?)", score, now.strftime("%d/%m/%Y"), username, id)
        except IndexError:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO `bests` (`score`, `date`, `username`, `id`) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (score, now.strftime("%d/%m/%Y"), username, id,))
                connection.commit()
    connection.close()
    return

def get_bests():
    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT `score`, `username`, `date` FROM `bests` ORDER BY `score` DESC LIMIT 5"
            cursor.execute(sql)
            bests = cursor.fetchone()
    connection.close()
    return bests

