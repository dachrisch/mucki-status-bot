# coding=UTF-8
from flask import Flask, render_template

from sheet import retrieve_team_status

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/status")
def status():
    return render_template('status.html',
                           status=retrieve_team_status())


if __name__ == '__main__':
    app.run()
