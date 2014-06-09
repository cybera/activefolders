class TransferTransport(object):
    def __init__(self, transfer):
        self._transfer = transfer

    def start_transfer(self):
        raise NotImplementedError

    def stop_transfer(self):
        raise NotImplementedError

    def transfer_success(self):
        raise NotImplementedError


class ExportTransport(object):
    CREDENTIALS = []

    def __init__(self, folder_destination):
        self._folder_destination = folder_destination

    def start_export(self):
        raise NotImplementedError

    def results_available(self):
        raise NotImplementedError

    def get_results(self):
        raise NotImplementedError

    def export_success(self):
        raise NotImplementedError
