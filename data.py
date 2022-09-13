import csv
import os
import datetime

from flask import Flask, flash, redirect, render_template, request, session
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

db = SQL("sqlite:///constituencies.db")

def make_constituencies():
    database = []
    with open("data.csv", mode="r", encoding="UTF-8", newline="") as f:
        reader = csv.DictReader(f)
        for count, row in enumerate(reader):
            database.append({
                "Constituency": row["Constituency"],
                "MP": row["Name"],
                "Party": row["Party"]
            })
    for count, constituency in enumerate(database):
        db.execute("INSERT INTO constituencies (id, constituency, MP, party) VALUES (?, ?, ?, ?)",
                   count, constituency["Constituency"], constituency["MP"], constituency["Party"])