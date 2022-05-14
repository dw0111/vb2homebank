#! /usr/bin/env python3

from builtins import ResourceWarning
import unittest
import os
import warnings
import tempfile
import subprocess
import vb2homebank


class Vb2HomebankTest(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def testShouldConvertCashFile(self):
        with open(r'testfiles/test.csv', encoding='utf_8') as csv_file:
            vb2homebank.convert_vb_cash(csv_file, 'testresult.csv')
            csv_file.seek(0)
            lineNumber = len(vb2homebank.find_transaction_lines(csv_file))
            self.assertEqual(lineNumber, 3)

    def testShouldConvertCashFileAndWriteToAlternativeOutputDir(self):
        with open(r'testfiles/test.csv', encoding='utf_8') as csv_file:
            tmpdir = tempfile.gettempdir()
            vb2homebank.convert_vb_cash(csv_file,
                                        os.path.join(tmpdir, "testresult.csv"))

    def tearDown(self):
        self.delete('testresult.csv')

    def delete(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)


class Vb2HomebankFunctionalTest(unittest.TestCase):

    def testShouldRunScript(self):
        result = subprocess.run(["./vb2homebank.py", "testfiles/test.csv"])
        self.assertEqual(0, result.returncode)

    def testShouldRunScriptWithOutputParameter(self):
        result = subprocess.run([
            "./vb2homebank.py", "testfiles/test.csv", "--output-file",
            "/tmp/testresult.csv"
        ])
        self.assertEqual(0, result.returncode)

    def tearDown(self):
        default_output_name = 'converted_test.csv'
        self.delete(default_output_name)

    def delete(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)


if __name__ == '__main__':
    unittest.main()
