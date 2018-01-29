from flask import Flask

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    app.logger.debug('Hier spricht der Debugger.')
    return 'Hello world!'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
