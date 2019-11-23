import flask
import sqlite3
from flask import jsonify, Response
from config import DEBUG, DATABASE_PATH
from models import Application, ApplicationHistory

app = flask.Flask(__name__)
app.config["DEBUG"] = DEBUG


@app.route('/<app_id>', methods=['GET'])
def application(app_id):
    connection = sqlite3.connect(DATABASE_PATH)
    application = Application.from_app_id(app_id, connection)
    if application is not None:
        return jsonify(application.to_json())
    return jsonify({
        'error': f'Application with {app_id} not found'
    }), 204


app.run()
