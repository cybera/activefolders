from threading import Thread
import activefolders.requests as requests


class Transport(Thread):
    def __init__(self):
        super().__init__()
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
        _add_folder_to_dtn()
        _transfer()
        _transfer_complete()

    def _transfer(self):
        raise NotImplementedError

    def _add_folder_to_dtn(self):
        folder = self._transfer.folder
        dtn = self._transfer.dtn
        dtn_conf = conf.dtns[dtn]
        request = requests.AddFolderRequest(dtn_conf, folder)

        LOG.info("Adding folder {} to {}".format(folder.uuid, dtn_conf['api']))
        resp = request.execute()

        if resp.status_code == 200 or resp.status_code == 201:
            return 0
        else:
            LOG.error("Adding folder {} to {} failed with error: {}".format(folder.uuid, dtn_conf['api'], resp.text))
            return 1 

    def _transfer_complete(self):
        LOG.debug("Transfer {} complete, informing destination DTN".format(transfer.id))
        request = requests.StartTransfersRequest(dtn_conf, folder)
        resp = request.execute()
        if resp.status_code == 200:
            return 0
        else:
            LOG.error("DTN did not acknowledge transfer complete for transfer {}".format(transfer.id))
            return 1


class DestinationTransport(Transport):
    def __init__(self, export, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._export = export

    def _start_transport(self):
        _export()

    def _export(self):
        raise NotImplementedError


class ResultsTransport(Transport):
    def __init__(self, folder_destination, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._folder_destination = folder_destination

    def _start_transport(self):
        result_files = self._folder_destination.result_files
        if result_files is None:
            self._auto_results()
        else:
            self._results()

    def _auto_results(self):
        raise NotImplementedError

    def _results(self):
        raise NotImplementedError
