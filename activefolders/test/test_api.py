from uuid import uuid4
import http.client
import json
import unittest as test
import activefolders.db as db
import activefolders.api as api
import activefolders.test.utils as utils

class ApiTest(test.TestCase):
    conn = None
    uuids = None

    def setUpClass(self):
        utils.set_test_config()
        db.init()
        api.start()

    def setUp(self):
        self.conn = http.client.HTTPConnection('localhost', 8080)
        self.uuids = None

    def request_and_response(self, expected_status, method, url, body=None, headers={}):
        self.conn.request(method, url, body, headers)
        resp = self.conn.getresponse()
        self.assertEqual(resp.status, expected_status)
        body = resp.read()
        return json.loads(body)

    def test_folders(self):
        folders = self.request_and_response(200, 'GET', '/folders')
        self.assertEqual(len(folders), 0)
        self.uuids = utils.populate_database()
        folders = self.request_and_response(200, 'GET', '/folders')
        self.assertEqual(len(folders), len(self.uuids))

    def test_folder(self):
        uuid = uuid4()
        self.request_and_response(404, 'GET', '/folders/{}'.format(uuid))
        self.uuids = utils.populate_database()
        self.request_and_response(200, 'GET', '/folders/{}'.format(self.uuids[0]))

    def test_add_folder(self):
        uuid = uuid4()
        self.request_and_response(201, 'POST', '/folders/{}'.format(uuid))
        self.request_and_response(200, 'GET', '/folders/{}'.format(uuid))
        self.request_and_response(403, 'POST', '/folders/{}'.format(uuid))
        self.request_and_response(400, 'POST', '/folders/0')

    def test_delete_folder(self):
        uuid = uuid4()
        self.request_and_response(404, 'DELETE', '/folders/{}'.format(uuid))
        utils.populate_database()
        self.request_and_response(200, 'DELETE', '/folders/{}'.format(self.uuids[0]))

    def test_transfer(self):
        pass
