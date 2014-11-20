from threading import Thread
import activefolders.requests as requests
import activefolders.conf as conf


class Transport(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._success = False
        self._exception = None

    def run(self):
        try:
            self._start_transport()
            self._success = True
        except Exception as e:
            self._exception = e

    def _start_transport(self):
        raise NotImplementedError

    @property
    def success(self):
        return self._success

    @property
    def exception(self):
        return self._exception


class DtnTransport(Transport):
    def __init__(self, transfer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transfer = transfer

    def _start_transport(self):
        self._add_folder_to_dtn()
        self._start_transfer()
        self._transfer_complete()

    def _start_transfer(self):
        raise NotImplementedError

    def _add_folder_to_dtn(self):
        folder = self._transfer.folder
        dtn = self._transfer.dtn
        request = requests.AddFolderRequest(dtn=dtn, folder=folder)

        resp = request.execute()
        if not request.success:
            raise requests.UnexpectedResponse(resp)

    def _transfer_complete(self):
        folder = self._transfer.folder
        dtn = self._transfer.dtn
        email = self._transfer.email
        request = requests.StartTransfersRequest(dtn=dtn, folder=folder, email=email)

        resp = request.execute()
        if not request.success:
            raise requests.UnexpectedResponse(resp)


class DestinationTransport(Transport):
    def __init__(self, export, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._folder_destination = export.folder_destination

    def _start_transport(self):
        self._start_export()

    def _start_export(self):
        raise NotImplementedError


class ResultsTransport(Transport):
    def __init__(self, folder_destination, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._folder_destination = folder_destination
        self._new_results = None

    def _start_transport(self):
        result_files = self._folder_destination.result_files
        if result_files is None:
            self._new_results = self._get_auto_results()
        else:
            self._new_results = self._get_results()

    def _get_auto_results(self):
        raise NotImplementedError

    def _get_results(self):
        raise NotImplementedError

    @property
    def new_results(self):
        return self._new_results
