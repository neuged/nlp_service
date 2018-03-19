import os
import copy
from classes.service_error import ServiceError
from idai_journals.publications import TextAnalyzer

from flask import Flask, jsonify, request, url_for
from celery_client import celery

app = Flask('nlp_service')
app.debug = True

KNOWN_OPERATIONS = ["NER", "POS"]
KNOWN_LANGUAGES = ['de', 'en', 'it', 'fr']
DEFAULT_PARAMS = {
    "include_references": True
}


@app.route('/')
def index():
    app.logger.debug('Hello world! Says the debug logger...')
    return 'Hello Wolfgang!'


@app.route('/annotate_celery/<operation>', methods=['POST'])
def annotate_celery(operation):
    try:
        request.get_data()
        input_text = request.data.decode('utf-8')
        params = _parse_request_params(request.args)
        params['operation'] = _parse_annotation_operation(operation)
        task = celery.send_task('annotate', args=[input_text, params], kwargs={})

        return jsonify({}), 202, {'Location': url_for('task_status', task_id=task.id)}
    except ServiceError as error:
        return error.build()


def _parse_request_params(request_params):
    params = copy.copy(DEFAULT_PARAMS)
    if "lang" in request_params:
        if request.args["lang"] in KNOWN_LANGUAGES:
            params['lang'] = request_params['lang']
        else:
            raise ServiceError("Language '%s' not supported." % request_params["lang"])

    if "include-references" in request_params:
        if request_params["include-references"] == "True":
            params["include_references"] = True
        elif request_params["include-references"] == "False":
            params["include_references"] = False
        else:
            params = DEFAULT_PARAMS["include_references"]

    return params


def _parse_annotation_operation(requested_operation):

    if requested_operation == 'all':
        return KNOWN_OPERATIONS

    if requested_operation in KNOWN_OPERATIONS:
        return requested_operation
    else:
        raise ServiceError('Unknown operation: %s.' % requested_operation, 400)


@app.route('/annotate/<operation>', methods=['POST'])
def annotate(operation):
    try:
        text_analyzer = _create_text_analyzer(request)
        content = dict({})
        params = copy.copy(DEFAULT_PARAMS)
        params["operation"] = operation
        _set_up_params_and_text_analyzer(request, params, text_analyzer)
        _run_operation(content, params, text_analyzer)
        _add_metadata(content, params, text_analyzer)
        return jsonify(content)
    except ServiceError as error:
        return error.build()


@app.route('/get-entities/', methods=['POST'], defaults={'entity_type': ""})
@app.route('/get-entities/<entity_type>', methods=['POST'])
def get_entities(entity_type):
    try:
        text_analyzer = _create_text_analyzer(request)
        content = dict({})
        params = copy.copy(DEFAULT_PARAMS)
        params["entity_type"] = entity_type
        _set_up_params_and_text_analyzer(request, params, text_analyzer)
        _get_entities_from_text(content, params, text_analyzer)
        _add_metadata(content, params, text_analyzer)
        return jsonify(content)
    except ServiceError as error:
        return error.build()


@app.route('/list-languages')
def list_languages():
    # @ TODO get drom TextAnalyzer
    return jsonify(KNOWN_LANGUAGES)


def _get_entities_from_text(content, params, text_analyzer):
    list = text_analyzer.get_entities(text_analyzer.do_ner(), params["entity_type"], params["include_references"])
    content["entities"] = [e.to_json() for e in list]


def _create_text_analyzer(request):
    request.get_data()
    input_text = request.data.decode('utf-8')
    if len(input_text) < 30:
        raise ServiceError('Input is not long enough to parse. It must be at least 30 characters', 400)
    return TextAnalyzer(str(input_text))


def _run_operation(content, params, textAnalyzer):
    operation = params["operation"]
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


def _set_up_params_and_text_analyzer(request, params, text_analyzer):
    if "lang" in request.args:
        if request.args["lang"] in KNOWN_LANGUAGES:
            text_analyzer.lang = request.args["lang"]
        else:
            raise ServiceError("language '%s' not supported." % request.args["lang"])
    if "include-references" in request.args:
        params["include_references"] = _parameter_to_boolean(request.args["include-references"], params["include_references"])
    if "entity_type" in params:
        if params["entity_type"] == "":
            params["entity_type"] = []
        elif params["entity_type"] not in text_analyzer.SUPPORTED_ENTITY_TYPES.keys():
            raise ServiceError("entity type '%s' not supported!" % params["entity_type"])
        else:
            params["entity_type"] = [text_analyzer.SUPPORTED_ENTITY_TYPES[params["entity_type"]]]


def _parameter_to_boolean(param, default_value):
    if param in ["false", "False", "FALSE", "0", "Off", "off", "OFF", "NO", "no", "No", 0, False]:
        return False
    if param in ["true", "True", "TRUE", "1", "On", "on", "ON", "YES", "yes", "Yes", 1, True]:
        return True
    return default_value


@app.route('/longtask', methods=['POST'])
def long_task():
    task = celery.send_task('long_task', args=[], kwargs={})
    app.logger.debug(task.id)
    return jsonify({}), 202, {'Location': url_for('task_status', task_id=task.id)}


@app.route('/status/<task_id>')
def task_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
