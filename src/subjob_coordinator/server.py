"""The main entrypoint for running the Flask server."""
import flask
import os
import re
import time
from uuid import uuid4
import traceback
import jsonschema
import jsonschema.exceptions
from flask_session import Session

from . import schemas

app = flask.Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', True)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', str(uuid4()))
app.config['SESSION_TYPE'] = 'filesystem'
app.url_map.strict_slashes = False  # allow both `get /v1/` and `get /v1`
Session(app)


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
    # Initialize some session data if it's not present
    if 'provenance' not in flask.session:
        init_provenance()
    if 'job_statuses' not in flask.session:
        flask.session['job_statuses'] = {}  # type: dict
    # Validate the JSON body data using jsonschema
    json_data = flask.request.json
    jsonschema.validate(json_data, schemas.request_rpc)
    (module, method) = json_data['method'].split('.')
    if module == 'CallbackServer':
        if method == 'status':
            return flask.jsonify({'state': 'OK'})
        elif method == 'get_provenance':
            return get_provenance()
    else:
        # Given: 'AssemblyUtil._save_assembly_as_fasta_submit'
        # sub_methods will be ('save_assembly_as_fasta',)
        sub_methods = re.match(r'^_(.+)_submit$', method)
        if sub_methods:
            sub_method = sub_methods.groups()[0]
            context = json_data['context']
            return start_subjob(module, sub_method, context)
        elif method == '_check_job':
            jsonschema.validate(json_data, schemas.check_job_method)
            job_id = json_data['params'][0]
            return check_subjob(job_id)
    return (flask.jsonify({'error': 'Unknown method'}), 400)


def check_subjob(job_id):
    if job_id not in flask.session['job_statuses']:
        resp = {'error': 'No such job with ID ' + job_id}
        return (flask.jsonify(resp), 400)
    else:
        status = flask.session['job_statuses'][job_id]
        resp = {'status': status}
        return flask.jsonify(resp)


def start_subjob(module, method, context):
    # TODO run async process to pull image from docker hub
    #      then build and launch the container with the parameters
    #      and finally update job statuses with results
    flask.session['provenance']['subactions'].append({
        'name': module + '.' + method,
        'ver': context['service_ver'],
        'code_url': '<url>',  # TODO
        'commit': '<hash>'  # TODO
    })
    job_id = str(uuid4())
    flask.session['job_statuses'][job_id] = 'pending'
    return flask.jsonify({"job_id": job_id})


def init_provenance():
    # Setting the current running module data from the env. Not sure if this is the right approach.
    flask.session['provenance'] = {
        'epoch': time.time() * 1000,
        'description': 'KBase SDK method run via the KBase Execution Engine',
        'service': os.environ['SERVICE_NAME'],
        'method': os.environ['SERVICE_METHOD'],
        'service_ver': os.environ['SERVICE_VERSION'],
        'method_params': os.environ['METHOD_PARAMS'],
        'input_ws_objects': os.environ['INPUT_WORKSPACE_REFS'],
        'subactions': []
    }


def get_provenance():
    return flask.jsonify(flask.session['provenance'])


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
