from uuid import uuid4
from webtest import TestApp
import unittest as test
import activefolders.db as db
import activefolders.api as api
import activefolders.test.utils as testutils


class ApiTest(test.TestCase):
    app = TestApp(api.app)
    uuids = None

    @classmethod
    def setUpClass(cls):
        testutils.set_test_config()
        db.init()

    def tearDown(self):
        testutils.clear_database()
        self.uuids = None

    def request_and_response(self, expected_status, method, url):
        resp = self.app.request(url, method=method, expect_errors=True)
        self.assertEqual(resp.status_int, expected_status)
        return resp

    def test_folders(self):
        self.uuids = testutils.populate_database(5)
        folders = self.request_and_response(200, 'GET', '/folders').json
        self.assertEqual(len(folders['folders']), len(self.uuids))

    def test_folder(self):
        uuid = uuid4().hex
        self.request_and_response(404, 'GET', '/folders/{}'.format(uuid))
        self.app.get('/folders/{}'.format(uuid), status=404)
        self.assertEqual
        self.uuids = testutils.populate_database(1)
        self.request_and_response(200, 'GET', '/folders/{}'.format(self.uuids[0]))

    def test_add_folder(self):
        uuid = uuid4().hex
        self.request_and_response(201, 'POST', '/folders/{}'.format(uuid))
        self.request_and_response(200, 'GET', '/folders/{}'.format(uuid))
        self.request_and_response(403, 'POST', '/folders/{}'.format(uuid))
        self.request_and_response(400, 'POST', '/folders/0')

    def test_delete_folder(self):
        uuid = uuid4().hex
        self.request_and_response(404, 'DELETE', '/folders/{}'.format(uuid))
        self.request_and_response(201, 'POST', '/folders/{}'.format(uuid))
        self.request_and_response(200, 'DELETE', '/folders/{}'.format(uuid))

    def test_transfer(self):
        pass
