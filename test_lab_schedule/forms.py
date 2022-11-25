from django import forms
from .models import LabTestInfo, Machine, People
from .widget import DatePickerInput

tests = LabTestInfo.objects.all()
machines = Machine.objects.all()
technicians = People.objects.filter(role='TC')

TEST_RESULTS = (
        ('QUEUE', 'Test Queue'),
        ('PASS', 'Meets Criteria'),
        ('FAIL', 'Does Not Meet Criteria'),
        ('RND', 'R&D Test Complete'),
        ('CANCEL', 'Cancelled'),
    )

class TestForm(forms.Form):
    lims = forms.CharField()
    labtestinfo = forms.ModelChoiceField(queryset=tests ,label='Test')
    machine = forms.ModelChoiceField(queryset=machines)
    technician = forms.ModelChoiceField(queryset=technicians)
    start_date = forms.DateField(widget=DatePickerInput())
    end_date = forms.DateField(widget=DatePickerInput())

class EditTestForm(forms.Form):
    machine = forms.ModelChoiceField(queryset=machines)
    technician = forms.ModelChoiceField(queryset=technicians)
    start_date = forms.DateField(widget=DatePickerInput())
    end_date = forms.DateField(widget=DatePickerInput())
    result = forms.ChoiceField(choices=TEST_RESULTS)

