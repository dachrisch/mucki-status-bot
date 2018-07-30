# coding=UTF-8
import os
from multiprocessing import Process

from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, url_for, redirect, send_from_directory

from sheet import retrieve_team_status
from sheets import SheetConnector
from yammer import YammerConnector

executor = ThreadPoolExecutor(1)

app = Flask(__name__)
server = None

flow = None


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/status')
def status():
    return render_template('status.html',
                           status=retrieve_team_status())


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
        retrieve_team_status()
    except Exception, e:
        return 'error during Sheet connection: [%s]' % e.message, 503

    try:
        SheetConnector.get_credentials()
    except Exception, e:
        return 'error during Credentials: [%s]' % e.message, 503

    try:
        YammerConnector().alive()
    except Exception, e:
        return 'error during Yammer connection: [%s]' % e.message, 503

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
    start_server()
