import os

from django.test import TestCase
from ..models import Part, BomBike
from ..bom_import import Csv_Importer

CWD = os.getcwd()
TEST_FILE_DIR = os.path.join(CWD, "reports", "tests", "test_files")

class BomImporterTests(TestCase):

    def setUp(self):
        csv = os.path.join(TEST_FILE_DIR, "wrangled_bom.csv")
        self.importer = Csv_Importer(uploaded_file=csv)

    def test_is_csv(self):
        self.assertTrue(self.importer.is_csv())

    def test_read_file(self):
        self.assertTrue(self.importer.read_file())

    def test_determine_type(self):
        self.importer.read_file()
        self.importer.determine_type()
        self.assertEquals(self.importer.csv_type, "bom")

    def test_check_document_length(self):
        self.importer.read_file()
        total_lines = 0
        for row in self.importer.reader:
            total_lines += 1
        # csv file is 2107 lines long, but the first one is a header, so actual length is 2106
        self.assertEqual(total_lines, 2106)

    def test_get_pid(self):
        self.importer.read_file()
        dictionary_list = list(self.importer.reader)
        first_dict = dictionary_list[0]
        self.assertEqual(first_dict["PID"], '221468')

    def test_get_model(self):
        self.importer.read_file()
        dictionary_list = list(self.importer.reader)
        first_dict = dictionary_list[0]
        self.assertEqual(first_dict["MODEL"], "AETHOS COMP")

    def test_get_size(self):
        self.importer.read_file()
        dictionary_list = list(self.importer.reader)
        first_dict = dictionary_list[0]
        self.assertEqual(first_dict["SIZE"], "49")

    def test_import_all(self):
        # First create the invalid, missing, and none parts
        Part.objects.create(description="INVALID", agile_number="0000000001")
        Part.objects.create(description="MISSING", agile_number="0000000002")
        Part.objects.create(description="NONE", agile_number="0000000003")
        self.importer.read_file()
        self.importer.determine_type()
        self.importer.import_all()