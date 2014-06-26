from __future__ import absolute_import
from requests_futures.sessions import FuturesSession
import json
import requests
import activefolders.conf as conf


class Request(object):
    _session = FuturesSession()

    def __init__(self, dtn_conf, command):
        self._url = dtn_conf['api'] + command

    def execute(self):
        raise NotImplementedError


class GetRequest(Request):
    def __init__(self, dtn_conf, command):
        super(GetRequest, self).__init__(dtn_conf, command)

    def execute(self):
        resp = requests.get(self._url)
        return resp


class PostRequest(Request):
    def __init__(self, dtn_conf, command, data=None):
        super(PostRequest, self).__init__(dtn_conf, command)
        self._headers = { 'Content-type': 'application/json' }
        self._data = json.dumps(data)

    def execute(self):
        resp = requests.post(self._url, data=self._data, headers=self._headers)
        return resp


class CheckResultsRequest(GetRequest):
    def __init__(self, dtn_conf, folder):
        command = "/folders/{}/check_results".format(folder.uuid)
        super(CheckResultsRequest, self).__init__(dtn_conf, command)

    def execute(self):
        self._session.get(self._url)


class StartTransfersRequest(PostRequest):
    def __init__(self, dtn_conf, folder):
        command = "/folders/{}/start_transfers".format(folder.uuid)
        super(StartTransfersRequest, self).__init__(dtn_conf, command)


class AddFolderRequest(PostRequest):
    def __init__(self, dtn_conf, folder):
        destinations = {}
        for folder_dst in folder.destinations:
            destinations[folder_dst.destination] = {
                'credentials': folder_dst.credentials,
                'result_files': folder_dst.result_files
            }

        data = {
            'uuid': folder.uuid,
            'home_dtn': conf.settings['dtnd']['name'],
            'destinations': destinations
        }

        if folder.results:
            folder_dst = folder.results_for
            data['results_for'] = {
                'folder': folder_dst.folder.uuid,
                'destination': folder_dst.destination
            }

        super(AddFolderRequest, self).__init__(dtn_conf, '/add_folder', data)
