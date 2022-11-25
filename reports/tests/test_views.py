import os
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

CSV = reverse('reports:csv_upload')
CWD = os.getcwd()
TEST_FILE_DIR = os.path.join(CWD, "reports", "tests", "test_files")

class CsvUploadForm(TestCase):

    def setUp(self):
        self.c = Client()

    def test_get_page(self):
        response = self.c.get(CSV)
        self.assertTrue(response.status_code == 200)

    def test_correct_template(self):
        response = self.c.get(CSV)
        self.assertEqual(response.templates[0].name, 'reports/csv_upload.html')

    def test_post_data(self):
        file_path = os.path.join("reports", "tests", "test_files", "parts.csv")
        with open(file_path) as f:
            response = self.c.post(CSV, {'attachment':f, 'file_type':'parts'}, format="multipart/form-data")
        self.assertEqual(response.status_code, 200)

    def test_invalid_csv_upload_redirect(self):
        file_path = os.path.join("reports", "tests", "test_files", "work_tracking.xlsx")
        with open(file_path, encoding='utf-8', errors='replace') as f:
            response = self.c.post(CSV, {'attachment':f, 'file_type':'parts'}, format="multipart/form-data")
        self.assertEqual(response.status_code, 302)

        