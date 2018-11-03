"""The main entrypoint for running the Flask server."""
import flask
import os
import re
from uuid import uuid4
import traceback
import json
import jsonschema
import jsonschema.exceptions

from . import schemas

app = flask.Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', True)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', str(uuid4()))
app.url_map.strict_slashes = False  # allow both `get /v1/` and `get /v1`


@app.route('/', methods=['GET', 'POST'])
def root():
    """
    Main request handler.
    This roughly follows JSON RPC 1.1: https://jsonrpc.org/historical/json-rpc-1-1-wd.html
    Methods:
    - "CallbackServer.get_provenance"
    - "CallbackServer.status"
    - "<Module>._<method>_submit"
    - "<Module>._check_job"

    In 'Module._check_job', 'Module' is discarded because we just use the job ID.

    In 'Module._<method>_submit', we extract out the <method> name
    """
    json_data = json.loads(flask.request.get_data())
    jsonschema.validate(json_data, schemas.request_rpc)
    req_id = json_data.get('id', str(uuid4()))
    (module, method) = json_data['method'].split('.')
    params = json_data.get('params')
    resp = {
        'id': req_id,
        'module': module,
        'method': method,
        'params': params
    }
    if module == 'CallbackServer':
        if method == 'status':
            resp['state'] = 'OK'
        elif method == 'get_provenance':
            # TODO
            resp['action_to_take'] = 'provenance'
    else:
        # Given: 'AssemblyUtil._save_assembly_as_fasta_submit'
        # sub_methods will be ('save_assembly_as_fasta',)
        sub_methods = re.match(r'^_(.+)_submit$', method)
        if sub_methods:
            # TODO start subjob
            resp['action_to_take'] = 'submit_subjob'
            resp['submethod'] = sub_methods.groups()[0]
        elif method == '_check_job':
            # TODO check subjob by id
            jsonschema.validate(json_data, schemas.check_job_method)
            resp['job_id'] = json_data['params'][0]
            resp['action_to_take'] = 'check_job'
    return flask.jsonify(resp)


@app.errorhandler(jsonschema.exceptions.ValidationError)
def validation_error(err):
    """Json Schema validation error."""
    resp = {
        'error': str(err).split('\n')[0],
        'instance': err.instance,
        'validator': err.validator,
        'validator_value': err.validator_value,
        'schema': err.schema
    }
    return (flask.jsonify(resp), 400)


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
    """Simple debug log of each request's response."""
    if os.environ.get('FLASK_DEBUG'):
        print('=' * 80)
        print(' '.join([flask.request.method, flask.request.path]))
        print('Body: ' + flask.request.get_data().decode())
        print(response.status)
    return response


if __name__ == '__main__':
    app.run(port=0)
