from __future__ import absolute_import
import json
import requests
import activefolders.conf as conf


class Request:
    def __init__(self, dtn_conf, command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._url = dtn_conf['api'] + command

    def execute(self):
        raise NotImplementedError


class GetRequest(Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self):
        resp = requests.get(self._url)
        return resp


class PostRequest(Request):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headers = { 'Content-type': 'application/json' }
        self._data = json.dumps(data)

    def execute(self):
        resp = requests.post(self._url, data=self._data, headers=self._headers)
        return resp


class StartTransfersRequest(PostRequest):
    def __init__(self, folder, *args, **kwargs):
        command = "/folders/{}/start_transfers".format(folder.uuid)
        super().__init__(command=command, *args, **kwargs)


class AddFolderRequest(PostRequest):
    def __init__(self, folder, *args, **kwargs):
        destinations = {}

        for folder_dst in folder.destinations:
            destinations[folder_dst.destination] = {
                'credentials': folder_dst.credentials,
                'result_files': folder_dst.result_files,
                'check_for_results': folder_dst.check_for_results
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

        super().__init__(data=data, command='/add_folder', *args, **kwargs)


class UnexpectedResponse(Exception):
    def __init__(self, response, *args, **kwargs):
        super().__init__(response.text, *args, **kwargs)
