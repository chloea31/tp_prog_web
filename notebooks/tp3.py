#!usr/bin/python3
#-*-coding: utf-8-*-

import sqlite3
from flask import Flask
from flask.helpers import url_for
from flask.scaffold import F
from werkzeug.utils import send_file
from flask import send_file
from flask import request

###################
### Q1 and 2
###################

app=Flask(__name__)

@app.route("/td1/<filename>")
@app.route("/td1/")
def content_file(filename="index.html"):
    with open(f"fichiers/td1/{filename}", "r") as filename:
        f = filename.read()
    try:
        return send_file(f"fichiers/td1/{filename}", attachment_filename=filename)
    except Exception as e:
        return str(e)

###################
### Q3
###################

@app.route("/formproc", methods=["POST"])
def print_message():
    return("Vos données ont bien été prises en compte")

###################
### Q4, 5 and 7
###################

@app.route("/formproc", methods=["POST"])
def print_message():
    data = request.from
    conn = sqlite3.connect("db.sqlite3")
    try:
        c = conn.cursor()
        c.execute(f"INSERT INTO FormData VALUES ('{data['prenom']}', '{data['nom']}', '{data['genre']}')")
        conn.commit()
    finally:
        conn.close()
    return (f"""
    <table border="black">
        <tr>
            <td>Nom</td>
            <td>{data["nom"]}</td>
        </tr>
        <tr>
            <td>Prénom</td>
            <td>{data["prenom"]}</td>
        </tr>
        <tr>
            <td>Genre</td>
            <td>{data["genre"]}</td>
        </tr>
    </table>
    <a href="{url_for('personnesBDD')}">Personnes inscrites</a>
    """)

##################
### Q6
##################

@app.route("/inscrits")
def personnesBDD():
    liste_pers = []
    conn = sqlite3.connect("db.sqlite3")
    try:
        c = conn.cursor()
        c.execute("""SELECT * FROM FormData""")

        rows = c.fetchall()

        for row in rows:
            liste_pers.append(row)

    finally:
        conn.close()
    return (f"""<p>{liste_pers}</p><br/><a href="{url_for('content_file', filename='form.html')}">Personnes ajoutees</a>""")

##################
### Q7
##################


