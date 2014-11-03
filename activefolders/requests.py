from __future__ import absolute_import
from requests.auth import HTTPBasicAuth
import json
import requests
import activefolders.conf as conf
import activefolders.db as db


class Request:
    def __init__(self, dtn, command, method, headers=None, params=None, data=None, expected_responses=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dtn_conf = conf.dtns[dtn]
        self._dtn = dtn
        self._command = command
        self._url = dtn_conf['api'] + command
        self._method = method
        self._headers = headers
        self._params = params
        self._data = data
        self._expected_responses = expected_responses if expected_responses is not None else []
        self._success = None

    def execute(self, *args, **kwargs):
        secret = conf.settings['dtnd']['root_secret']
        try:
            resp = requests.request(self._method,
                                    self._url,
                                    headers=self._headers,
                                    params=self._params,
                                    data=json.dumps(self._data),
                                    auth=HTTPBasicAuth(secret, None),
                                    verify=False,  # Ignore certificate errors
                                    *args, **kwargs)
        except requests.ConnectionError:
            resp = None

        if resp is None or resp.status_code not in self._expected_responses:
            self._success = False
        else:
            self._success = True

        return resp

    def execute_with_monitoring(self, *args, **kwargs):
        """ If initial request fails retry later using monitoring system """
        self.execute(*args, **kwargs)
        if not self.success:
            db.Request.create(method=self._method,
                              dtn=self._dtn,
                              command=self._command,
                              headers=self._headers,
                              params=self._params,
                              data=self._data,
                              expected_responses=self._expected_responses)

    @property
    def expected_responses(self):
        return self._expected_responses

    @property
    def success(self):
        return self._success


class GetRequest(Request):
    def __init__(self, *args, **kwargs):
        super().__init__(method='GET', *args, **kwargs)


class PostRequest(Request):
    def __init__(self, headers=None, *args, **kwargs):
        if headers is None:
            headers = { 'Content-type': 'application/json' }
        else:
            headers['Content-type'] = 'application/json'
        super().__init__(method='POST', headers=headers, *args, **kwargs)


class DeleteRequest(Request):
    def __init__(self, *args, **kwargs):
        super().__init__(method='DELETE', *args, **kwargs)


class StartTransfersRequest(PostRequest):
    def __init__(self, folder, *args, **kwargs):
        command = "/folders/{}/start_transfers".format(folder.uuid)
        expected_responses = [ 200 ]
        super().__init__(command=command, expected_responses=expected_responses, *args, **kwargs)


class AddFolderRequest(PostRequest):
    def __init__(self, folder, *args, **kwargs):
        expected_responses = [ 200, 201 ]
        destinations = {}

        for folder_dst in folder.destinations:
            destinations[folder_dst.destination] = {
                'credentials': folder_dst.credentials,
                'result_files': folder_dst.result_files,
                'check_for_results': folder_dst.check_for_results,
                'results_destination': folder_dst.results_destination,
                'results_credentials': folder_dst.results_credentials
            }

        data = {
            'uuid': folder.uuid,
            'home_dtn': conf.settings['dtnd']['name'],
            'destinations': destinations
        }

        if folder.results:
            folder_dst = folder.results_for.get()
            data['results_for'] = {
                'folder': folder_dst.folder.uuid,
                'destination': folder_dst.destination
            }

        super().__init__(data=data, command='/add_folder', expected_responses=expected_responses, *args, **kwargs)


class DeleteFolderRequest(DeleteRequest):
    def __init__(self, folder, *args, **kwargs):
        command = "/folders/{}".format(folder.uuid)
        expected_responses = [ 200, 404 ]
        super().__init__(command=command, expected_responses=expected_responses, *args, **kwargs)


class AddDestinationRequest(PostRequest):
    def __init__(self, folder, destination, *args, **kwargs):
        command = "/folders/{}/destinations".format(folder.uuid)
        expected_responses = [ 200, 404 ]
        params = { 'dst': destination }
        folder_destination = db.FolderDestination.get(folder=folder, destination=destination)
        data = {}
        data['credentials'] = folder_destination.credentials
        data['result_files'] = folder_destination.result_files
        data['check_for_results'] = folder_destination.check_for_results
        data['results_destination'] = folder_destination.results_destination
        data['results_credentials'] = folder_destination.results_credentials
        super().__init__(command=command, params=params, data=data, expected_responses=expected_responses, *args, **kwargs)


class RemoveDestinationRequest(DeleteRequest):
    def __init__(self, folder, destination, *args, **kwargs):
        command = "/folders/{}/destinations".format(folder.uuid)
        expected_responses = [ 200, 404 ]
        params = { 'dst': destination }
        super().__init__(command=command, params=params, expected_responses=expected_responses, *args, **kwargs)


class UnexpectedResponse(Exception):
    def __init__(self, response, *args, **kwargs):
        if response is None:
            msg = "No response received"
        else:
            msg = response.text
        super().__init__(msg, *args, **kwargs)
