#/usr/bin/python3
#-*-coding: utf-8-*-

from flask import Flask

app = Flask(__name__)

@app.route("/greeting")
def root():
    return "Hello world"


