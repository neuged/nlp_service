import os

from classes.service_error import ServiceError

from flask import Flask, jsonify, request
from pymongo import MongoClient
from idai_journals.publications import TextAnalyzer

app = Flask(__name__)
app.debug = True

KNOWN_OPERATIONS = ["NER", "POS"]
KNOWN_LANGUAGES = ['de', 'en', 'it', 'fr']


@app.route('/')
def index():
    app.logger.debug('Hello world! Says the debug logger...')

    return 'Hello Wolfgang!'


@app.route('/annotate/<operation>', methods=['POST'])
def annotate(operation):
    try:
        text_analyzer = _create_text_analyzer(request)
        content = dict({})
        _configure_text_analyzer(request, text_analyzer)
        _run_operation(content, operation, text_analyzer)
        _add_metadata(content, text_analyzer)
        return jsonify(content)
    except ServiceError as error:
        return error.build()


@app.route('/database_info')
def database_info():
    credentials = os.environ['DB_ROOT_CREDENTIALS']
    host = os.environ['DB_HOST']
    mongo_client = MongoClient('mongodb://' + credentials + '@' + host)
    app.logger.debug(mongo_client.server_info())
    return jsonify(mongo_client.server_info())


@app.route('/listLanguages')
def list_languages():
    # @ TODO implement
    return jsonify(KNOWN_LANGUAGES)


def _create_text_analyzer(request):
    request.get_data()
    input_text = request.data.decode('utf-8')
    if len(input_text) < 30:
        raise ServiceError('Input is not long enough to parse. It must be at least 30 characters', 400)
    app.logger.debug(request.args)
    return TextAnalyzer(str(input_text))


def _run_operation(content, operation, textAnalyzer):

    if operation not in KNOWN_OPERATIONS:
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


def _configure_text_analyzer(request, text_analyzer):
    if "lang" in request.args:
        if request.args["lang"] in KNOWN_LANGUAGES:
            text_analyzer.lang = request.args["lang"]
        else:
            raise ServiceError("language '%s' not supported." % request.args["lang"])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
