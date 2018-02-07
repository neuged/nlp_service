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

    if len(input_text) < 30:
        return build_error('Input is not long to parse. It must be at least 30 characters', 400)


    app.logger.debug(request.args)

    textAnalyzer = TextAnalyzer(str(input_text))

    if request.args["lang"] :
        textAnalyzer.lang = request.args["lang"]

    if operation == "NER":
        content = dict({
            "named_entites": textAnalyzer.NER()
        })
    elif operation == "POS":
        content = dict({
            "part_of_speech_tags": textAnalyzer.pos_tag()
        })
    elif operation == "ALL":
        content = dict({
            "part_of_speech_tags": textAnalyzer.pos_tag(),
            "named_entites": textAnalyzer.NER()
        })
    else:
        return build_error('Invalid operation: %s' % operation, 400)

    meta = dict({
        "detected_language": textAnalyzer.lang,
        "word_count": len(textAnalyzer.words),
        "sentence_count": len(textAnalyzer.sentences)
    })

    content["meta"] = meta

    return jsonify(content), 200


@app.route('/database_info')
def database_info():
    credentials = os.environ['DB_ROOT_CREDENTIALS']
    host = os.environ['DB_HOST']
    mongo_client = MongoClient('mongodb://' + credentials + '@' + host)

    app.logger.debug(mongo_client.server_info())

    return jsonify(mongo_client.server_info())


def build_error(message, code = 400) :
    return jsonify(dict ({
        "message": message,
        "code": code
    })), code

if __name__ == '__main__':
    app.run(host='0.0.0.0')
