import os
import unittest
import requests
import json

url = 'http://localhost:' + os.environ.get('CALLBACK_SERVER_PORT', '4176')


class TestServer(unittest.TestCase):

    def test_invalid_method(self):
        """Test invalid HTTP methods."""
        data = {'x': 'y'}
        resp = requests.put(url, data=json.dumps(data)).json()
        self.assertEqual(resp, {'error': '405 - Method not allowed.'})
        resp = requests.delete(url, data=json.dumps(data)).json()
        self.assertEqual(resp, {'error': '405 - Method not allowed.'})

    def test_invalid_rpc(self):
        """Test various invalid RPC data structures."""
        data1 = {'x': 'y'}
        resp = requests.post(url, data=json.dumps(data1)).json()
        self.assertEqual(resp['error'], "'method' is a required property")
        data2 = {'method': 'y', 'params': []}
        resp = requests.post(url, data=json.dumps(data2)).json()
        self.assertTrue("'y' does not match" in resp['error'])
        data3 = {'method': 'x.y', 'params': []}
        resp = requests.post(url, data=json.dumps(data3))
        self.assertTrue('error' not in resp)
        self.assertEqual(resp.status_code, 200)

    def test_submit_job(self):
        """
        Test where the method is Module._method_submit to start a new job.
        """
        data = {
            'method': 'Module._method_submit',
            'params': []
        }
        resp = requests.post(url, data=json.dumps(data)).json()
        self.assertEqual(resp['action_to_take'], 'submit_subjob')
        self.assertEqual(resp['submethod'], 'method')

    def test_server_status(self):
        """Test where the method is to check the server status."""
        data = {'method': 'CallbackServer.status'}
        resp = requests.post(url, data=json.dumps(data)).json()
        self.assertEqual(resp['state'], 'OK')

    def test_get_provenance(self):
        """
        Test where the method is CallbackServer.get_provenance.
        """
        data = {'method': 'CallbackServer.get_provenance'}
        resp = requests.post(url, data=json.dumps(data)).json()
        self.assertEqual(resp['action_to_take'], 'provenance')

    def test_check_job_invalid_params(self):
        """The ._check_job method requires a certain params format."""
        # Missing params
        data1 = {'method': 'Xyz._check_job'}
        resp = requests.post(url, data=json.dumps(data1)).json()
        self.assertEqual(resp['error'], "'params' is a required property")
        # Empty type
        data2 = {'method': 'Xyz._check_job', 'params': []}
        resp = requests.post(url, data=json.dumps(data2)).json()
        self.assertEqual(resp['error'], '[] is too short')

    def test_check_job(self):
        """
        Test where the method is 'XYZ._check_job' with [job_id] for the params
        """
        data = {'method': 'Xyz._check_job', 'params': ['1']}
        resp = requests.post(url, data=json.dumps(data)).json()
        self.assertEqual(resp['job_id'], '1')
        self.assertEqual(resp['action_to_take'], 'check_job')
