# coding=UTF-8
import os
import sys
import traceback

from flask import Flask, render_template, request, url_for, redirect
from concurrent.futures import ThreadPoolExecutor

from sheet import retrieve_team_status
from sheets import SheetConnector

executor = ThreadPoolExecutor(1)

app = Flask(__name__)


class BotLogger(object):
    def __init__(self):
        self.__stream = None

    def dump(self):
        if self.__stream:
            return self.__stream.read()
        else:
            return ''

    def listen(self, stream):
        self.__stream = stream


bot_log = BotLogger()
flow = None


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/status')
def status():
    return render_template('status.html',
                           status=retrieve_team_status())


@app.route('/telegram', methods=['GET', 'POST'])
def telegram():
    if request.method == "POST":
        token = request.form['token']
        executor.submit(run_bot, token)
    return render_template('telegram.html', log=bot_log.dump())


@app.route('/sheets/authenticate', methods=['GET', 'POST'])
def authenticate_sheets():
    if request.method == "POST":
        global flow
        flow = SheetConnector.flow(request.form['client_id'], request.form['client_secret'],
                                   url_for('callback', _external=True))
        return redirect(flow.step1_get_authorize_url())
    else:
        return render_template('oauth.html')


@app.route('/sheets/callback')
def callback():
    code = request.args.get('code')
    global flow
    credentials = flow.step2_exchange(code)
    SheetConnector.store(credentials)
    if SheetConnector.get_credentials().invalid:
        return "Failed"
    else:
        return "OK"


def run_bot(token):
    try:
        p = os.popen('TELEBOT_TOKEN=%s python bot.py' % token)
        bot_log.listen(p)
    except:
        traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
