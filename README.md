# nlp_service

This is a webservice exposing [nlp_components](https://github.com/dainst/nlp_components) functionality. 

It is split into two main modules: 
1) A [Flask](http://flask.pocoo.org/) app that hands over incoming requests to 
2) [Celery](http://www.celeryproject.org/) workers which do the actual processing and are using the `nlp_components`. 

The Celery module needs a [RabbitMQ](https://www.rabbitmq.com/) as its message Broker.

## Prerequisites

The easiest way to develop and/or deploy the service is to use the 
[nlp-service-docker](https://github.com/dainst/nlp-service-docker), which will pull all dependencies and setup 
everything automatically.

If you do not want to use Docker, these are the current prerequisites:

* A RabbitMQ instance
* Checked out and installed [nlp_components](https://github.com/dainst/nlp_components).
* Python 3

## Installation

Install the Python 3 dependencies as described in [worker/requirements](worker/requirements.txt) and 
[service/requirements](service/requirements.txt). For example by running `pip3 install worker/requirements` and 
`pip3 install worker/requirements.txt` from the root directory.

Celery needs to know how to connect to the RabbitMQ message broker and expects the following environment variables to 
be set accordingly:

```
BROKER_HOST
BROKER_USER
BROKER_PASSWORD
BROKER_VHOST
```

Add the following folders to your `PYTHONPATH` environment variable: The root directory of 
this repository and the root directory of `nlp_components`.

## Starting the service

The Flask app is started with:
 
`python3 main.py` from in the `service` directory.

The Flask app should be accessible at [localhost:5000](http://localhost:5000).

The worker(s) is started with:

`watchmedo auto-restart --recursive --patterns="*.py" -- celery -A celery_tasks worker --loglevel=info` from the worker
 directory. This will live-reload the worker when making changes to the worker scripts. 

If you do not want the live reload, just run `celery -A worker.celery_tasks worker --loglevel=info`

## REST API

See [API reference](API-REFERENCE.md).