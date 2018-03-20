import os

from celery import Celery
from idai_journals.publications import TextAnalyzer

broker_host = os.environ['BROKER_HOST']
broker_user = os.environ['BROKER_USER']
broker_password = os.environ['BROKER_PASSWORD']
broker_vhost = os.environ['BROKER_VHOST']

broker_config = 'amqp://' + broker_user + ':' + broker_password + '@' + broker_host + '/' + broker_vhost
result_config = 'rpc://'

celery = Celery('nlp_service', broker=broker_config, backend=result_config)


@celery.task(bind=True, name='annotate')
def annotate(self, input_text, params):
    text_analyzer = TextAnalyzer(input_text)
    if 'lang' in params:
        text_analyzer.lang = params['lang']
    self.update_state(state='PROGRESS',
                      meta={'status': 'Running NLP analysis...'})
    result = _run_annotation(text_analyzer, params)
    result = _add_metadata(result, text_analyzer)

    return {'result': result, 'status': 'Processing completed.'}


@celery.task(bind=True, name='get_entities')
def get_entities(self, input_text, params):
    text_analyzer = TextAnalyzer(input_text)
    if 'lang' in params:
        text_analyzer.lang = params['lang']
    self.update_state(state='PROGRESS',
                      meta={'status': 'Running NLP analysis...'})

    # TODO: This is somewhat ugly.
    # We should think about changing the Flask endpoint: You should be able to pass a list
    # of wanted entity types, which are parsed in Flask and passed to the worker as a list in the params dict.
    # Then we could just replace `exclusive_entity_type` by `params['requested_entity_types_list']`
    # or something similar here.
    if params['entity_type'] is not None:
        exclusive_entity_type = [text_analyzer.SUPPORTED_ENTITY_TYPES[params["entity_type"]]]
    else:
        exclusive_entity_type = []

    entity_list = \
        text_analyzer.get_entities(
            text_analyzer.do_ner(),
            exclusive_entity_type,
            params['include_references'])

    result = {'entity_list': [entity.to_json() for entity in entity_list]}
    result = _add_metadata(result, text_analyzer)

    return {'result': result, 'status': 'Processing completed.'}


def _run_annotation(text_analyzer, params):

    result = dict()

    if 'NER' in params['operation']:
        result['named_entities'] = text_analyzer.do_ner()
    if 'POS' in params['operation']:
        result['part_of_speech_tags'] = text_analyzer.do_pos_tag()

    return result


def _add_metadata(result, text_analyzer):
    return {
        **result,
        **dict({
            "detected_language": text_analyzer.lang,
            "word_count": len(text_analyzer.words),
            "sentence_count": len(text_analyzer.sentences)
        })
    }


# old tutorial code for celery
# @celery.task(bind=True, name='long_task')
# def long_task(self):
#     """Background task that runs a long function with progress reports."""
#     verbs = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
#     adjectives = ['master', 'radiant', 'silent', 'harmonic', 'fast']
#     nouns = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
#
#     message = ''
#
#     total = random.randint(10, 50)
#     for i in range(total):
#         if not message or random.random() < 0.25:
#             message = '{0} {1} {2}...'.format(random.choice(verbs),
#                                               random.choice(adjectives),
#                                               random.choice(nouns))
#         self.update_state(state='PROGRESS',
#                           meta={'current': i, 'total': total, 'status': message})
#
#         time.sleep(1)
#
#     return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42}
