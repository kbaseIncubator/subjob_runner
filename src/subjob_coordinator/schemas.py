
request_rpc = {
    'type': 'object',
    'required': ['method'],
    'properties': {
        'version': {'const': '1.1'},
        'method': {
            'type': 'string',
            'description': 'Module name and method name to run.',
            'example': 'AssemblyUtil.get_assembly_as_fasta',
            'pattern': '^\w+\.\w+$'
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
