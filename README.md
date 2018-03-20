# nlp_service

This is a webservice exposing [nlp_components](https://github.com/dainst/nlp_components) functionality. 

It is split into two main modules: 
1) A [Flask](http://flask.pocoo.org/) app that hands over incoming requests to 
2) [Celery](http://www.celeryproject.org/) workers which do the actual processing and are using the `nlp_components`. 

The Celery module needs a [RabbitMQ](https://www.rabbitmq.com/) as its message Broker.
