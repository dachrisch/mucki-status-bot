# coding=UTF-8
from flask import Flask, render_template, request
from concurrent.futures import ThreadPoolExecutor
from sheet import retrieve_team_status

executor = ThreadPoolExecutor(1)

app = Flask(__name__)


class BotLogger(object):
    def __init__(self):
        self.__stream = None

    def dump(self):
        return self.__stream

    def listen(self, stream):
        self.__stream = stream


bot_log = BotLogger()


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


def run_bot(token):
    import subprocess

    p = subprocess.Popen('TELEBOT_TOKEN=%s python2 bot.py' % token)
    bot_log.listen(p.communicate())


if __name__ == '__main__':
    app.run()
