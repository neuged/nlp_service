from classes.service_error import ServiceError

from flask import Flask, jsonify, request, url_for
from celery_client import celery

app = Flask('nlp_service')
app.debug = True

VALID_ANNOTATION_OPERATIONS = ["NER", "POS"]
VALID_ENTITY_TYPES = ["locations", "persons", "organisations"]  # as defined in nlp_components as SUPPORTED_ENTITY_TYPES
VALID_LANGUAGES = ['de', 'en', 'it', 'fr']
DEFAULT_PARAMS = {
    "include_references": True
}


@app.route('/')
def index():
    app.logger.debug('Hello Wolfgang! Says the debug logger...')
    return 'Hello Wolfgang!'


@app.route('/annotate/<operation>', methods=['POST'])
def annotate(operation):
    try:
        request.get_data()
        input_text = request.data.decode('utf-8')
        params = _parse_request_args(request.args)
        params['operation'] = _parse_annotation_operation(operation)
        task = celery.send_task('annotate', args=[input_text, params], kwargs={})

        return jsonify({'status': 'Accepted', 'task': task.id}),\
            202, {'Location': url_for('task_status', task_id=task.id)}

    except ServiceError as error:
        return error.build()


@app.route('/get-entities/', methods=['POST'], defaults={'entity_type': None})
@app.route('/get-entities/<entity_type>', methods=['POST'])
def get_entities(entity_type):
    try:
        request.get_data()
        input_text = request.data.decode('utf-8')
        params = _parse_request_args(request.args)
        params['entity_type'] = _validate_entity_type(entity_type)

        task = celery.send_task('get_entities', args=[input_text, params], kwargs={})

        return jsonify({'status': 'Accepted', 'task': task.id}),\
            202, {'Location': url_for('task_status', task_id=task.id)}

    except ServiceError as error:
        return error.build()


@app.route('/status/<task_id>')
def task_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status':
                'Task is waiting for execution or unknown. '
                'Any task id that’s not known is implied to be in the pending state. See: '
                'http://docs.celeryproject.org/en/latest/userguide/tasks.html#states'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@app.route('/help/', methods=['GET'], defaults={'request_type': None})
@app.route('/help/<request_type>', methods=['GET'])
def list_options(request_type):
    if request_type == 'annotation-operations':
        return jsonify(VALID_ANNOTATION_OPERATIONS)
    elif request_type == 'languages':
        return jsonify(VALID_LANGUAGES)
    elif request_type == 'entity-types':
        return jsonify(VALID_ENTITY_TYPES)
    else:
        return jsonify({
            'annotation-operations': VALID_ANNOTATION_OPERATIONS,
            'languages': VALID_LANGUAGES,
            'entity-types': VALID_ENTITY_TYPES,
        })


def _parse_request_args(args):
    params = {}
    if "lang" in args:
        if request.args["lang"] in VALID_LANGUAGES:
            params['lang'] = args['lang']
        else:
            raise ServiceError("Language '%s' not supported." % args["lang"])

    if "include-references" in args:
        if args["include-references"] == "True":
            params["include_references"] = True
        elif args["include-references"] == "False":
            params["include_references"] = False
        else:
            params["include_references"] = DEFAULT_PARAMS["include_references"]
    else:
        params["include_references"] = DEFAULT_PARAMS["include_references"]

    return params


def _parse_annotation_operation(requested_operation):

    if requested_operation == 'all':
        return VALID_ANNOTATION_OPERATIONS

    if requested_operation in VALID_ANNOTATION_OPERATIONS:
        return requested_operation
    else:
        raise ServiceError('Unknown operation: %s.' % requested_operation, 400)


def _validate_entity_type(entity_type):
    if entity_type not in VALID_ENTITY_TYPES and entity_type is not None:
        raise ServiceError("Entity type '%s' not supported." % entity_type)
    return entity_type


if __name__ == '__main__':
    app.run(host='0.0.0.0')


# old tutorial code for celery
# @app.route('/longtask', methods=['POST'])
# def long_task():
#     task = celery.send_task('long_task', args=[], kwargs={})
#     app.logger.debug(task.id)
#     return jsonify({}), 202, {'Location': url_for('task_status', task_id=task.id)}
#