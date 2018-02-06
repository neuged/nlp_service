import os

from flask import Flask, jsonify, request
from pymongo import MongoClient
from idai_journals.publications import TextAnalyzer

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    app.logger.debug('Hello world! Says the debug logger...')

    return 'Hello Wolfgang!'


@app.route('/annotate/<operation>', methods=['POST'])
def annotate(operation):

    request.get_data()

    input_text = request.data.decode('utf-8')

    result = TextAnalyzer(str(input_text))
    content = None

    if operation == "NER":
        content = jsonify(result.NER())
    elif operation == "POS":
        content = jsonify(result.pos_tag())
    elif operation == "ALL":
        content = \
            jsonify(dict ({
                "NER": result.NER(),
                "POS": result.pos_tag()
            }))
    else:
        content = 'Invalid operation: %s' % operation
        return content, 400

    return content, 200


@app.route('/database_info')
def database_info():
    credentials = os.environ['DB_ROOT_CREDENTIALS']
    host = os.environ['DB_HOST']
    mongo_client = MongoClient('mongodb://' + credentials + '@' + host)

    app.logger.debug(mongo_client.server_info())

    return jsonify(mongo_client.server_info())


if __name__ == '__main__':
    app.run(host='0.0.0.0')
