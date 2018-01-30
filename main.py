import os

from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    app.logger.debug('Hello world! Says the debug logger...')

    return 'Hello world!'


@app.route('/database_info')
def database_info():
    credentials = os.environ['DB_ROOT_CREDENTIALS']
    host = os.environ['DB_HOST']
    mongo_client = MongoClient('mongodb://' + credentials + '@' + host)

    app.logger.debug(mongo_client.server_info())

    return jsonify(mongo_client.server_info())


if __name__ == '__main__':
    app.run(host='0.0.0.0')
