import unittest as test
import os.path
from time import sleep
import hashlib
import activefolders.transports.gridftp_simple as transport


@test.skipUnless(os.path.isfile("/usr/bin/globus-url-copy"),
                 "No GridFTP binary found")
class TransferTest(test.TestCase):
    md5 = hashlib.md5()

    def setUp(self):
        self.src_file = "/tmp/test_gridftp_simple.1MiB"
        self.dst = "ftp://localhost:2811"
        self.dst_file = "/tmp/test_gridftp_simple.out"
        with open(self.src_file, "wb") as out:
            out.truncate(1 * 1024 * 1024)

    def test_transfer(self):
        proc = transport.start_transfer(src=self.src_file,
                                        dst=self.dst+self.dst_file)
        while transport.transfer_is_success(proc) is None:
            sleep(0.2)
        self.assertTrue(transport.transfer_is_success(proc))
        self.assertTrue(os.path.isfile(self.dst_file))

    def tearDown(self):
        os.remove(self.src_file)
        os.remove(self.dst_file)
