# coding=UTF-8
import os
from multiprocessing import Process

from flask import Flask, render_template, request, send_from_directory

from config import CONFIG_PATH, MUCKI_TRACKER_SHEET_ID
from google_service_api.welfare import WelfareStatus
from telegram_service.gif import random_gif_url
from my_logging import checked_load_logging_config
from google_service.sheets import SheetConnector
from yammer_service.yammer import YammerConnector

app = Flask(__name__)
server = None

flow = None


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/status')
def status():
    shout = WelfareStatus(SheetConnector(MUCKI_TRACKER_SHEET_ID)).shoutout
    return render_template('status.html',
                           status=WelfareStatus(SheetConnector(MUCKI_TRACKER_SHEET_ID)).team_name_status, shout=shout,
                           gif=random_gif_url(shout))


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', e)
    return render_template('500.html', error=str(e)), 500


@app.route('/kill')
def kill():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Shutting down..."


@app.route('/alive')
def alive():
    try:
        WelfareStatus(SheetConnector(MUCKI_TRACKER_SHEET_ID)).team_name_status
    except Exception as e:
        return 'error during Sheet connection: [%s]' % e, 503

    try:
        SheetConnector.get_credentials()
    except Exception as e:
        return 'error during Credentials: [%s]' % e, 503

    try:
        YammerConnector().alive()
    except Exception as e:
        return 'error during Yammer connection: [%s]' % e, 503

    return 'OK'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def start_server():
    global server
    server = Process(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080})
    server.start()


def kill_server():
    server.terminate()
    server.join()


if __name__ == '__main__':
    checked_load_logging_config(CONFIG_PATH)
    start_server()
