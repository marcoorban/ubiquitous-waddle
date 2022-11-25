from django.db import models
from datetime import date

from django.forms import ValidationError

class MfrPartName(models.Model):
    name = models.CharField(max_length=255, blank=False)

    def save(self, *args, **kwargs):
        # Prevents having a mfr part with an empty string as its name.
        if self.name == "":
            return
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Part(models.Model):
    agile_number = models.CharField(max_length=10, unique=True)
    lifecycle = models.CharField(max_length=16)
    description = models.CharField(max_length=512)
    part_type = models.CharField(max_length=64)
    names_list = models.ManyToManyField(MfrPartName, related_name='part')

    def __str__(self):
        return self.agile_number + " - " + self.description

    def get_names(self):
        return self.names_list.all()

    def get_bikes(self):
        if self.part_type == "Frame":
            return self.bikes_frame.all().order_by('production_date')
        elif self.part_type == "Fork":
            return self.bikes_fork.all().order_by('production_date')
        elif self.part_type == "Handlebars":
            return self.bikes_handlebar.all().order_by('production_date')
        elif self.part_type == "Stem":
            return self.bikes_stem.all().order_by('production_date')
        elif self.part_type == "Seat Post":
            return self.bikes_seatpost.all().order_by('production_date')
        elif self.part_type == "Saddle":
            return self.bikes_saddle.all().order_by('production_date')
        elif self.part_type == "Bottom Bracket":
            return self.bikes_bb.all().order_by('production_date')
        elif self.part_type == "Crank Set":
            return self.bikes_cs.all().order_by('production_date')

    def get_trcs(self):
        return self.trcs_used_in.all()

    def get_reports(self):
        reports = self.trps_used_in.all()
        if reports:
            return reports
        else:
            reports = []
            for project in self.sbc_project.all():
                temp = project.trp.all()
                for t in temp:
                    reports.append(t)
            if reports:
                return reports

    def has_report(self):
        reports = self.get_reports()
        if reports:
            return {
                "reports":[report for report in list(reports)],
                "lifecycle": self.get_lifecycle(reports)
            }
        return {
            "reports":"None",
            "lifecycle": "none"
        }

    def get_lifecycle(self, reports):
        for report in reports:
            if report.lifecycle == "Production":
                return "production"
            else:
                return "preliminary"

class TestReportPart(models.Model):
    agile_number = models.CharField(max_length=10, unique=True)
    lifecycle = models.CharField(max_length=16, default="Preliminary")
    report_type = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    part = models.ManyToManyField(Part, related_name='trps_used_in')
    created_date = models.DateField(default=date(1974,1,1))
    manufacturer = models.CharField(max_length=512, default="N/A")

    def __str__(self):
        return self.agile_number + " - " + self.description

class SbcProject(models.Model):
    agile_number = models.CharField(max_length=10)
    description = models.CharField(max_length=512, default="")
    trp = models.ManyToManyField(TestReportPart, related_name='sbc_project')
    tla = models.ManyToManyField(Part, related_name='sbc_project')

    def __str__(self):
        return self.agile_number + " - " + self.description

class TestReportCombo(models.Model):
    agile_number = models.CharField(max_length=10, unique=True)
    lifecycle = models.CharField(max_length=16, default="Preliminary")
    report_type = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    trp = models.ManyToManyField(TestReportPart, related_name="trcs_used_in")
    part = models.ManyToManyField(Part, related_name="trcs_used_in")
    created_date = models.DateField(default=date(1974,1,1))

    def __str__(self):
        return self.agile_number + " - " + self.description

    def get_contents(self):
        trps = [trp for trp in self.trp.all()]
        parts = [part for part in self.part.all()]
        return {
            'parts':parts,
            'trps':trps
        }

class BikeReport(models.Model):
    pid = models.CharField(max_length=6)
    agile_number = models.CharField(max_length=10)
    first_prod_date = models.DateField(default=date(1974,1,1))
    description = models.CharField(max_length=512)
    has_attachment = models.BooleanField(default=False)
    ebike = models.BooleanField(default=False)
    trp_list = models.ManyToManyField(TestReportPart, related_name='br_trp')
    trc_list = models.ManyToManyField(TestReportCombo, related_name='br_trc')

    def __str__(self):
        return self.agile_number + "-" + self.description[0:15]

    def get_trps(self):
        return self.trp_list.all()

    def get_trcs(self):
        return self.trc_list.all()

    def is_ebike(self):
        return self.ebike

class BomBike(models.Model):
    model = models.CharField(max_length=256)
    size = models.CharField(max_length=4)
    frame = models.ForeignKey(Part, null=True, on_delete=models.PROTECT, related_name="bikes_frame")
    fork = models.ForeignKey(Part, null=True, on_delete=models.PROTECT, related_name="bikes_fork")
    handlebar = models.ForeignKey(Part, null=True, on_delete=models.PROTECT, related_name="bikes_handlebar")
    stem = models.ForeignKey(Part, null=True, on_delete=models.PROTECT, related_name="bikes_stem")
    seatpost = models.ForeignKey(Part, null=True, on_delete=models.PROTECT, related_name="bikes_seatpost")
    saddle = models.ForeignKey(Part, null=True, on_delete=models.PROTECT, related_name="bikes_saddle")
    bb = models.ForeignKey(Part, null=True, on_delete=models.PROTECT, related_name="bikes_bb")
    cs = models.ForeignKey(Part, null=True, on_delete=models.PROTECT, related_name="bikes_cs")
    report = models.ForeignKey(BikeReport, null=True, on_delete=models.PROTECT, related_name='bombike')
    production_date = models.DateField(null=True)

    def __str__(self):
        return self.model  + " " + self.size

    def get_prod_year(self):
        return str(self.production_date).split('-')[0]

    def clean_model(self):
        """Removes all whitespace. We need to remove whitespace to use the bike model in the url"""
        return self.model.strip().replace(" ", "")

    def get_hbstem_reports(self):
        reports = []
        hbreports = self.handlebar.trps_used_in.all()
        stemreports = self.stem.trps_used_in.all()
        for hbreport in hbreports:
            for stemreport in stemreports:
                results = TestReportCombo.objects.filter(trp=stemreport).filter(trp=hbreport)
                for result in results:
                    reports.append(result)
        return reports

    def get_sdlstp_reports(self):
        reports = []
        spreports = self.seatpost.trps_used_in.all()
        for spreport in spreports:
            results = TestReportCombo.objects.filter(part=self.saddle).filter(trp=spreport)
            for result in results:
                reports.append(result)
        return reports

    def get_bbc_reports(self):
        reports = TestReportCombo.objects.filter(part=self.bb).filter(part=self.cs).all()
        return reports

    def has_hbstem_trc(self):
        reports =  self.get_hbstem_reports()
        if reports:
            return {
                "reports":[report for report in reports],
                "lifecycle": self.get_lifecycle(reports)
            }
        return {
            "reports":"None",
            "lifecycle":"none"
        }

    def has_sdlstp_trc(self):
        reports =  self.get_sdlstp_reports()
        if reports:
            return {
                "reports":[report for report in reports],
                "lifecycle": self.get_lifecycle(reports)
            }
        return {
            "reports":"None",
            "lifecycle":"none"
        }

    def has_bbc_trc(self):
        reports =  self.get_bbc_reports()
        if reports:
            return {
                "reports":[report for report in reports],
                "lifecycle": self.get_lifecycle(reports)
            }
        return {
            "reports":"None",
            "lifecycle":"none"
        }

    def get_lifecycle(self, reports):
        for report in reports:
            if report.lifecycle == "Production":
                return "production"
            else:
                return "preliminary"

    def get_frame(self):
        return self.frame

    def get_fork(self):
        return self.fork

    def get_steerer(self):
        return self.handlebar, self.stem

    def get_seating(self):
        return self.seatpost, self.saddle

    def get_bbcs(self):
        return self.bb, self.cs





