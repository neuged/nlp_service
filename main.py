import os

from flask import Flask, jsonify, request
from pymongo import MongoClient
from idai_journals.publications import TextAnalyzer

app = Flask(__name__)
app.debug = True

KNOWN_OPERATIONS = ["NER", "POS"]



@app.route('/')
def index():
    app.logger.debug('Hello world! Says the debug logger...')

    return 'Hello Wolfgang!'



@app.route('/annotate/<operation>', methods=['POST'])
def annotate(operation):

    request.get_data()
    input_text = request.data.decode('utf-8')
    if len(input_text) < 30:
        return _build_error('Input is not long enough to parse. It must be at least 30 characters', 400)
    app.logger.debug(request.args)
    textAnalyzer = TextAnalyzer(str(input_text))

    content = dict({})
    _configure_text_analyzer(request.args, textAnalyzer)
    _run_operation(content, operation, textAnalyzer)
    _add_metadata(content, textAnalyzer)
    return jsonify(content), 200



@app.route('/database_info')
def database_info():

    credentials = os.environ['DB_ROOT_CREDENTIALS']
    host = os.environ['DB_HOST']
    mongo_client = MongoClient('mongodb://' + credentials + '@' + host)
    app.logger.debug(mongo_client.server_info())
    return jsonify(mongo_client.server_info())



def _run_operation(content, operation, textAnalyzer):

    if not operation in KNOWN_OPERATIONS:
        operation = "all"

    content["operation"] = operation

    if operation in ["NER", "all"]:
        content["named_entites"] = textAnalyzer.NER()

    if operation in ["POS", "all"]:
        content["part_of_speech_tags"] = textAnalyzer.pos_tag()

    return content


def _add_metadata(content, textAnalyzer):
    content["meta"] = dict({
        "detected_language": textAnalyzer.lang,
        "word_count": len(textAnalyzer.words),
        "sentence_count": len(textAnalyzer.sentences)
    })


def _add_warning(content, message):
    try:
        content["warnings"].append(message)
    except NameError:
        content["warnings"] = []


def _build_error(message, code = 400):
    return jsonify(dict ({
        "message": message,
        "code": code
    })), code


def _configure_text_analyzer(args, textAnalyzer):
    if request.args["lang"] :
        textAnalyzer.lang = request.args["lang"]


if __name__ == '__main__':
    app.run(host='0.0.0.0')
