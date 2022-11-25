from datetime import timedelta, date
from django.db import models
from django.core.exceptions import ValidationError

def is_technician(value):
    person = People.objects.get(pk=value)
    print(person.role)
    # Will reject people that are not technicians
    if person.role != 'TC':
        raise ValidationError(
            ('%(value)s is not a technician'),
            params={'value':value}
        )

class LabTestInfo(models.Model):
    test_full_name = models.CharField(max_length=255)
    test_acronym = models.CharField(max_length=32)
    standard = models.CharField(max_length=255, blank=True)
    work_instruction = models.CharField(max_length=10, blank=True)
    report_form = models.CharField(max_length=10, blank=True)
    test_duration_in_days = models.IntegerField()

    def __str__(self):
        return self.test_acronym

class Machine(models.Model):
    name = models.CharField(max_length=2, blank=False, null=False)
    capable_tests = models.ManyToManyField(LabTestInfo, blank=True)
    is_online = models.BooleanField()

    def __str__(self):
        return self.name

class People(models.Model):
    TECHNICIAN = 'TC'
    STAKEHOLDER = 'SH'
    DEVELOPER = 'DV'
    COMPLIANCE = 'CP'
    DESIGN_ENGINEER = 'DE'

    ROLES = [
        (TECHNICIAN, 'Technician'),
        (STAKEHOLDER, 'Stakeholder'),
        (DEVELOPER, 'Developer'),
        (COMPLIANCE, 'Compliance'),
        (DESIGN_ENGINEER, 'Design Engineer')
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField(default="morban@specialized.com")
    role = models.CharField(max_length=255, choices=ROLES)

    def __str__(self):
        return self.name

class Bike(models.Model):
    model_year = models.IntegerField()
    bike_model = models.CharField(max_length=255)

    def __str__(self):
        return 'MY' + str(self.model_year) + ' ' + self.bike_model

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    stakeholders = models.ManyToManyField(People)

    def __str__(self):
        return self.name

class Sample(models.Model):
    bike_model = models.ManyToManyField(Bike)
    part1 = models.CharField(max_length=255)
    part2 = models.CharField(max_length=255, blank=True, default='')
    part1_dimensions = models.CharField(max_length=255, blank=True)
    part2_dimensions = models.CharField(max_length=255, blank=True)
    part1_agile = models.CharField(max_length=10)
    part2_agile = models.CharField(max_length=10, blank=True, null=True)
    part1_manu = models.CharField(max_length=255)
    part2_manu = models.CharField(max_length=255, blank=True, null=True)
    expected_completion_date = models.DateField(blank=True, null=True)
    reporter = models.ForeignKey(People, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        if self.part2:
            return self.part1 + ' / ' + self.part2
        else:
            return self.part1

class Test(models.Model):
    TEST_RESULTS = (
        ('QUEUE', 'Test Queue'),
        ('PASS', 'Meets Criteria'),
        ('FAIL', 'Does Not Meet Criteria'),
        ('RND', 'R&D Test Complete'),
        ('CANCEL', 'Cancelled'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    labtestinfo = models.ForeignKey(LabTestInfo, on_delete=models.PROTECT)
    result = models.CharField(max_length=255, choices=TEST_RESULTS, default=('QUEUE'))
    lims = models.CharField(max_length=10)
    start_date = models.DateField()
    end_date = models.DateField()
    machine = models.ForeignKey(Machine, null=True, on_delete=models.PROTECT)
    technician = models.ForeignKey(People, null=True, on_delete=models.PROTECT, validators=[is_technician])

    def calculate_end_date(self):
        days = timedelta(days=self.labtestinfo.test_duration_in_days)
        return self.start_date + days

    def get_reporter(self):
        return self.sample.reporter

    def is_delayed(self):
        if self.result == 'QUEUE':
            if self.end_date > date.today():
                return True

    def __str__(self):
        return 'LIMS-' + self.lims + ' --- ' + self.labtestinfo.test_acronym +  ' --- MACHINE ' + self.machine.name
