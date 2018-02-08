import os

from classes.service_error import ServiceError

from flask import Flask, jsonify, request
from pymongo import MongoClient
from idai_journals.publications import TextAnalyzer

app = Flask(__name__)
app.debug = True

KNOWN_OPERATIONS = ["NER", "POS"]
KNOWN_LANGUAGES = ['de', 'en', 'it', 'fr']
DEFAULT_PARAMS = {
    "include_references": False
}


@app.route('/')
def index():
    app.logger.debug('Hello world! Says the debug logger...')
    return 'Hello Wolfgang!'


@app.route('/annotate/<operation>', methods=['POST'])
def annotate(operation):
    try:
        text_analyzer = _create_text_analyzer(request)
        content = dict({})
        params = DEFAULT_PARAMS
        _configure_text_analyzer(request, params, text_analyzer)
        _run_operation(content, operation, text_analyzer)
        _add_metadata(content, params, text_analyzer)
        return jsonify(content)
    except ServiceError as error:
        return error.build()


@app.route('/get-entities/<entity_type>', methods=['POST'])
def get_entities(entity_type):
    try:
        text_analyzer = _create_text_analyzer(request)
        content = dict({})
        params = DEFAULT_PARAMS
        params["entity_type"] = entity_type
        _configure_text_analyzer(request, params, text_analyzer)
        _get_entities_from_text(content, params, text_analyzer)
        _add_metadata(content, params, text_analyzer)
        return jsonify(content)
    except ServiceError as error:
        return error.build()


@app.route('/database-info')
def database_info():
    credentials = os.environ['DB_ROOT_CREDENTIALS']
    host = os.environ['DB_HOST']
    mongo_client = MongoClient('mongodb://' + credentials + '@' + host)
    app.logger.debug(mongo_client.server_info())
    return jsonify(mongo_client.server_info())


@app.route('/list-languages')
def list_languages():
    # @ TODO implement
    return jsonify(KNOWN_LANGUAGES)


def _get_entities_from_text(content, params, text_analyzer):
    list = text_analyzer.get_entities(text_analyzer.do_ner(), ["ORG"], params["include_references"])
    content["entities"] = [e.to_json() for e in list]
    app.logger.debug(list[0].to_json())


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
        content["named_entities"] = textAnalyzer.do_ner()
    if operation in ["POS", "all"]:
        content["part_of_speech_tags"] = textAnalyzer.do_pos_tag()
    return content


def _add_metadata(content, params, textAnalyzer):
    content["meta"] = dict({
        "detected_language": textAnalyzer.lang,
        "word_count": len(textAnalyzer.words),
        "sentence_count": len(textAnalyzer.sentences)
    })


def _configure_text_analyzer(request, params, text_analyzer):
    if "lang" in request.args:
        if request.args["lang"] in KNOWN_LANGUAGES:
            text_analyzer.lang = request.args["lang"]
        else:
            raise ServiceError("language '%s' not supported." % request.args["lang"])
    if "include-references" in request.args:
        params["include_references"] = request.args["include-references"] not in ["false", "False", "FALSE", "0", "Off", "off"]


if __name__ == '__main__':
    app.run(host='0.0.0.0')
