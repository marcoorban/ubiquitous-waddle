import os

from django.test import TestCase
from django.urls import reverse
from datetime import date
from ..models import BikeReport, MfrPartName, TestReportCombo, TestReportPart, Part
from ..importers import Csv_Importer

CWD = os.getcwd()
TEST_FILE_DIR = os.path.join(CWD, "reports", "tests", "test_files")

class CsvImportGeneralTests(TestCase):

    def setUp(self):
        csv = os.path.join(TEST_FILE_DIR, "parts.csv")
        self.importer = Csv_Importer(uploaded_file=csv)
        self.importer.read_file()

    def test_is_csv(self):
        good_importer = self.importer
        self.assertTrue(good_importer.is_csv())

    def test_is_not_csv(self):
        pdf = os.path.join(TEST_FILE_DIR, "pdf.pdf")
        bad_importer = Csv_Importer(uploaded_file=pdf)
        self.assertFalse(bad_importer.is_csv())

    def test_read_correct_length(self):
        """Checks if it is counting the correct number of rows of the test csv file (there are fifteen rows in the test file)"""
        for row in self.importer.reader:
            pass
        self.assertEqual(self.importer.reader.line_num, 14)

    def test_determine_type_parts(self):
        self.importer.determine_type()
        self.assertEqual(self.importer.csv_type, "parts")

    def test_fake_header(self):
        bad = os.path.join(TEST_FILE_DIR, "fake_header.csv")
        bad_header = Csv_Importer(uploaded_file=bad)
        bad_header.read_file()
        bad_header.determine_type()
        self.assertEqual(bad_header.csv_type, "unknown")

    def test_remove_non_ascii(self):
        cleaned = self.importer.remove_non_ascii("Ø28.6mmxØ30.05,Ø9,700C")
        self.assertEqual(cleaned, "28.6mmx30.05,9,700C")

    def test_add_zeroes(self):
        number = '123'
        self.assertEqual(self.importer.add_zeroes(number), '0000000123')

    def test_date(self):
        date_str = "05/02/2017 12:32:40 AM CST"
        tdate = self.importer.convert_to_date(date_str)
        self.assertIsInstance(tdate, date)
        self.assertEqual(date(2017,5,2), tdate)


class CsvImportImportPart(TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        csv = os.path.join(TEST_FILE_DIR, "parts.csv")
        self.importer = Csv_Importer(uploaded_file=csv)
        self.importer.read_file()

    def test_import_line(self):
        self.importer.determine_type()
        for row in self.importer.reader:
            self.importer.import_line(row)
        part = Part.objects.get(agile_number="0000001455")
        self.assertEqual(len(part.names_list.all()), 2)
        self.assertEqual(part.lifecycle, "Support")
        part2 = Part.objects.get(agile_number="0000002773")
        self.assertEqual(part2.lifecycle, "Sell Down")
        self.assertEqual(len(part2.names_list.all()), 0)

    def test_import_part(self):
        MfrPartName.objects.create(name="Thing 1")
        row1 = {
            'Number':'1234567890',
            'Description':'Test Part',
            'Lifecycle Phase':'Production',
            'Part Type':'Frame',
            'Mfr. Part Number (Manufacturers)':'Thing 1'
        }
        row2 = {
            'Number':'1234567890',
            'Description':'Test Part',
            'Lifecycle Phase':'Production',
            'Part Type':'Frame',
            'Mfr. Part Number (Manufacturers)':'Thing 123'
        }
        self.importer.import_part(row1)
        self.importer.import_part(row2)
        test_part = Part.objects.get(agile_number="1234567890")
        self.assertEqual(test_part.description, "Test Part")
        self.assertEqual(test_part.lifecycle, "Production")
        self.assertEqual(len(test_part.get_names()), 2)

    def test_import_part_non_ascii_name(self):
        row1 = {
            'Number':'1234567890',
            'Description':'Back Sweep: 11°',
            'Lifecycle Phase':'Production',
            'Part Type':'Frame',
            'Mfr. Part Number (Manufacturers)':'Thing 1'
        }
        self.importer.import_part(row1)
        test_part = Part.objects.get(agile_number="1234567890")
        self.assertEqual(test_part.description, 'Back Sweep: 11')


class CsvImportImportTrp(TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        csv = os.path.join(TEST_FILE_DIR, "trps.csv")
        self.importer = Csv_Importer(uploaded_file=csv)
        self.importer.read_file()
        self.importer.determine_type()

    def test_determine_type(self):
        self.assertEqual(self.importer.csv_type, "trp")

    def test_read_correct_length(self):
        for row in self.importer.reader:
            # We want to iterate through all the lines but not do anything to them
            pass
        self.assertEqual(self.importer.reader.line_num, 16)

    def test_empty_item_number_toc(self):
        row = self.importer.reader.__next__()
        self.assertFalse(self.importer.import_line(row))

    def test_import_line(self):
        part_info_csv = os.path.join(TEST_FILE_DIR, "parts_for_trp_testing.csv")
        self.part_importer = Csv_Importer(uploaded_file=part_info_csv)
        self.part_importer.read_file()
        self.part_importer.determine_type()
        for row in self.part_importer.reader:
            self.part_importer.import_line(row)
        for row in self.importer.reader:
            self.importer.import_line(row)
        self.assertEqual(len(TestReportPart.objects.all()), 3)
        self.assertEqual(len(TestReportPart.objects.get(agile_number="0000190389").contents.all()), 4)

class CsvImportImportTrc(TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        csv = os.path.join(TEST_FILE_DIR, "trcs.csv")
        self.importer = Csv_Importer(uploaded_file=csv)
        self.importer.read_file()
        self.importer.determine_type()

    def test_determine_type(self):
        self.assertCountEqual(self.importer.csv_type, "trc")

    def test_read_correct_length(self):
        for row in self.importer.reader:
            # We want to iterate through all the lines but not do anything to them
            pass
        self.assertEqual(self.importer.reader.line_num, 12)

    def test_empty_item_number_toc(self):
        row = self.importer.reader.__next__()
        self.assertFalse(self.importer.import_line(row))

    def test_non_empty_item_number_toc(self):
        self.importer.reader.__next__()
        row = self.importer.reader.__next__()
        self.assertTrue(self.importer.import_line(row))

    def test_unknown_item_type(self):
        rows = []
        for row in self.importer.reader:
            rows.append(row)
        test_row = rows[-1]
        test_row["Item Type (TOC)"] = ""
        self.assertFalse(self.importer.import_line(rows[-1]))

    def test_part_content_type(self):
        rows = []
        for row in self.importer.reader:
            rows.append(row)
        test_row = rows[3]
        self.importer.import_line(test_row)
        trcs = TestReportCombo.objects.all()
        self.assertEqual(len(trcs), 1)
        trc = trcs[0]
        self.assertEqual(trc.agile_number, '0000143986')
        self.assertEqual(len(trc.part.all()), 1)
        part = trc.part.all()[0]
        self.assertEqual(part.agile_number, '0000080649')

    def test_trp_content_type(self):
        rows = []
        for row in self.importer.reader:
            rows.append(row)
        test_row = rows[2]
        self.importer.import_line(test_row)
        trcs = TestReportCombo.objects.all()
        self.assertEqual(len(trcs), 1)
        trc = trcs[0]
        self.assertEqual(trc.agile_number, '0000143986')
        self.assertEqual(len(trc.trp.all()), 1)
        trp = trc.trp.all()[0]
        self.assertEqual(trp.agile_number, '0000134733')

class CsvImportImportBig(TestCase):

    def test_import_trc(self):
        self.cwd = os.getcwd()
        csv = os.path.join(TEST_FILE_DIR, "trc_big.csv")
        self.importer = Csv_Importer(uploaded_file=csv)
        self.importer.read_file()
        self.importer.determine_type()
        for row in self.importer.reader:
            self.importer.import_line(row)
        trc = TestReportCombo.objects.get(agile_number='0000187152')
        self.assertEqual(len(trc.trp.all()),2)
        self.assertTrue(trc.trp.all()[0].agile_number, '0000187151')

    def test_import_trp(self):
        self.cwd = os.getcwd()
        csv = os.path.join(TEST_FILE_DIR, "trp_big.csv")
        self.importer = Csv_Importer(uploaded_file=csv)
        self.importer.read_file()
        self.importer.determine_type()
        for row in self.importer.reader:
            self.importer.import_line(row)
        print(len(TestReportPart.objects.all()))
        trp = TestReportPart.objects.get(agile_number="0000168768")
        self.assertEqual(len(trp.contents.all()), 4)
        self.assertEqual(trp.contents.all()[0].agile_number, '0000161593')

class CsvImportBikeReportToc(TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        csv = os.path.join(TEST_FILE_DIR, "bike_report_toc.csv")
        self.importer = Csv_Importer(uploaded_file=csv)
        self.importer.read_file()
        self.importer.determine_type()
        self.test_row = {
            "Number":"1111122222",
            "Description":"Test Bike",
            "Item Type (TOC)":"",
            "Item Number (TOC)":"1234567890"
        }
        BikeReport.objects.create(agile_number="1111122222", description="Test Bike Report")

    def test_reader_line_length(self):
        lines = 0
        for line in self.importer.reader:
            lines += 1
        self.assertEqual(lines, 3420)

    def test_import_trp(self):
        self.test_row["Item Type (TOC)"] = "Test Report Part"
        TestReportPart.objects.create(agile_number="1234567890")
        self.assertTrue(self.importer.import_bike_report_toc(self.test_row))
        bike_report = BikeReport.objects.get(agile_number="1111122222")
        self.assertEqual(len(bike_report.trp_list.all()), 1)
        self.assertEqual(bike_report.trp_list.all()[0].agile_number, "1234567890")

    def test_import_trc(self):
        self.test_row["Item Type (TOC)"] = "Test Report Combo"
        TestReportCombo.objects.create(agile_number="1234567890")
        self.assertTrue(self.importer.import_bike_report_toc(self.test_row))
        bike_report = BikeReport.objects.get(agile_number="1111122222")
        self.assertEqual(len(bike_report.trc_list.all()), 1)
        self.assertEqual(bike_report.trc_list.all()[0].agile_number, "1234567890")

    def test_import_content_empty_agile_number(self):
        self.test_row["Item Number (TOC)"] = ""
        self.assertFalse(self.importer.import_bike_report_toc(self.test_row))

    def test_import_unknown_toc_type(self):
        self.test_row["Item Type (TOC)"] = "Frame"
        self.assertFalse(self.importer.import_bike_report_toc(self.test_row))

    def test_correct_type(self):
        self.assertEqual(self.importer.csv_type, "bike_report_toc")


class CsvImportBikeReportInfo(TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        csv = os.path.join(TEST_FILE_DIR, "bike_report_info.csv")
        self.importer = Csv_Importer(uploaded_file=csv)
        self.importer.read_file()
        self.importer.determine_type()
        self.test_row = {
            "Number":"1234567890",
            "Description":"KENEVO INFO",
            "First Production Year (Page Three)":"2023",
            "First Production Month (Page Three)":"Jan",
            "Has Attachment (Attachments)":"Yes",
            "MPL Product ID (Don't Modify) (Page Three)":"123444"
        }

    def test_reader_line_length(self):
        lines = 0
        for line in self.importer.reader:
            lines += 1
        self.assertEqual(lines, 1539)

    def test_no_pid(self):
        self.test_row["MPL Product ID (Don't Modify) (Page Three)"] = ""
        self.assertFalse(self.importer.import_bike_report_info(self.test_row))

    def test_no_prodyear(self):
        self.test_row["First Production Year (Page Three)"] = ""
        self.assertFalse(self.importer.import_bike_report_info(self.test_row))

    def test_no_prodmonth(self):
        self.test_row["First Production Month (Page Three)"] = ""
        self.assertFalse(self.importer.import_bike_report_info(self.test_row))

    def test_import_line(self):
        self.assertTrue(self.importer.import_bike_report_info(self.test_row))

    def test_correct_info(self):
        self.assertTrue(self.importer.import_bike_report_info(self.test_row))
        bike_report = BikeReport.objects.get(agile_number="1234567890")
        self.assertEqual(bike_report.pid, "123444")
        self.assertEqual(bike_report.description, "KENEVO INFO")
        self.assertEqual(bike_report.first_prod_date, date(2023, 1, 1))
        self.assertEqual(bike_report.has_attachment, True)
        self.assertEqual(bike_report.ebike, True)

    def test_parse_date(self):
        testdate = date(2023, 3, 1)
        self.assertEqual(self.importer.parse_date("2023", "Mar"), testdate)

    def test_is_ebike(self):
        self.assertTrue(self.importer.is_ebike("2022 KENEVO"))
        self.assertTrue(self.importer.is_ebike("2022 LEVO"))
        self.assertTrue(self.importer.is_ebike("2022 VADO SL"))
        self.assertTrue(self.importer.is_ebike("2022 GLOBE"))
        self.assertTrue(self.importer.is_ebike("2022 HAUL"))
        self.assertTrue(self.importer.is_ebike("2022 VADO 3.0"))
        self.assertFalse(self.importer.is_ebike("2023 TARMAC SL8"))
        self.assertFalse(self.importer.is_ebike("2023 EPIC WC"))

    def test_correct_type(self):
        self.assertEqual(self.importer.csv_type, "bike_report_info")

