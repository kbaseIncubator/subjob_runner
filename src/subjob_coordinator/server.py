"""The main entrypoint for running the Flask server."""
import flask
import os
from uuid import uuid4
import traceback

app = flask.Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', True)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', str(uuid4()))
app.url_map.strict_slashes = False  # allow both `get /v1/` and `get /v1`


@app.route('/', methods=['GET'])
def root():
    """Server status."""
    return flask.jsonify({
        'it': 'works!'
    })


@app.errorhandler(404)
def page_not_found(err):
    return (flask.jsonify({'error': '404 - Not found.'}), 404)


@app.errorhandler(405)
def method_not_allowed(err):
    return (flask.jsonify({'error': '405 - Method not allowed.'}), 405)


# Any other unhandled exceptions -> 500
@app.errorhandler(Exception)
@app.errorhandler(500)
def server_error(err):
    print('=' * 80)
    print('500 Unexpected Server Error')
    print('-' * 80)
    traceback.print_exc()
    print('=' * 80)
    resp = {'error': '500 - Unexpected server error'}
    if os.environ.get('FLASK_DEBUG'):
        resp['error_class'] = err.__class__.__name__
        resp['error_details'] = str(err)
    return (flask.jsonify(resp), 500)


@app.after_request
def log_response(response):
    """Simple log of each request's response."""
    print(' '.join([flask.request.method, flask.request.path, '->', response.status]))
    return response
