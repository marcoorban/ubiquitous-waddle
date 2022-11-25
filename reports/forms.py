from django import forms
from django.core.validators import FileExtensionValidator
from datetime import date

class CsvUploadForm(forms.Form):
    file_type = forms.ChoiceField(
        choices=[
            ("bikebom", "Bike BOM"),
            ("parts", "Parts"),
            ("test_report_part", "Test Report Part"),
            ("test_report_combo", "Test Report Combo"),
            ("pid", "PID"),
            ("bike_reports", "Bike Reports"),
            ("bike_report_toc", "Bike Report TOC")
        ],
        required=False,
    )
    attachment = forms.FileField(validators=[FileExtensionValidator(["csv"])], required=False)

class BikeSearchForm(forms.Form):
    QUARTERS = (
        ("1-12", "All"),
        ("1-3", "Q1"),
        ("4-6", "Q2"),
        ("7-9", "Q3"),
        ("10-12", "Q4"),
    )
    ATTRS = {
        'class': 'form-check-inline',
        'style': 'margin-right: 0px; margin-left: 5px;'
    }
    this_year = date.today().year + 1
    bike_model = forms.CharField(max_length=50, required=False)
    production_year = forms.IntegerField(localize=False, required=False, initial=this_year)
    quarter = forms.ChoiceField(
        choices=QUARTERS,
        widget=forms.RadioSelect(attrs=ATTRS),
        required=False,
        initial=QUARTERS[0][0]
    )
