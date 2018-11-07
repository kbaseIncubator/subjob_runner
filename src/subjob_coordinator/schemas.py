"""
The full set of JSON schemas used for data validation and generation in this server.
"""


request_rpc = {
    'type': 'object',
    'required': ['method'],
    'properties': {
        'version': {'const': '1.1'},
        'method': {
            'type': 'string',
            'description': 'Module name and method name to run.',
            'example': 'AssemblyUtil.get_assembly_as_fasta',
            'pattern': r'^\w+\.\w+$'
        },
        'params': {
            'description': 'Parameters for the object. Can be any JSON data.'
        }
    }
}

# When the RPC method is XYZ._check_job
# We need params to be a singleton array of one job ID
check_job_method = {
    'type': 'object',
    'required': ['params'],
    'properties': {
        'params': {
            'type': 'array',
            'minItems': 1,
            'maxItems': 1,
            'items': [{
                'type': 'string',
                'title': 'Job ID to check.'
            }]
        }
    }
}

# Data representing all the context surrounding a new object being created from existing objects.
# The whole point of this is to provide data reproducibility.
provenance_action = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'time': {
            'type': 'string',
            'format': 'date-time',
            'description': 'The time this action was started.'
        },
        'epoch': {
            'type': 'integer',
            'description': 'The time this action was started.'
        },
        'service': {
            'type': 'string',
            'description': 'Name of the service/module performing the action.'
        },
        'service_ver': {
            'type': 'string',
            'description': 'Version of the service/module that performed this action.'
        },
        'method': {
            'type': 'string',
            'description': 'The method, function, or endpoint of the service/module that performed this action.'
        },
        'method_params': {
            'type': 'object',
            'description': 'The full set of parameters used when calling the method.'
        },
        'input_ws_objects': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': ('The workspace objects that were used as input to this action. '
                            'Typically, these will also be present as parts of the method_params. '
                            'A reference path into the object graph may be supplied.')
        },
        'description': {'type': 'string'},
        'subactions': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'name': {'type': 'string'},
                    'ver': {'type': 'string'},
                    'code_url': {'type': 'string', 'format': 'url'},
                    'commit': {'type': 'string'},
                    'endpoint_url': {'type': 'string'}
                }
            }
        }
    }
}
