from django.contrib import admin

from .models import Part, MfrPartName, TestReportPart, BomBike, TestReportCombo, BikeReport
from .models import SbcProject

class PartAdmin(admin.ModelAdmin):
    search_fields = ['description']
    list_filter = ['part_type']

class TestReportPartAdmin(admin.ModelAdmin):
    list_filter = ['report_type']
    list_display = ['agile_number', 'lifecycle', 'created_date']

class TestReportComboAdmin(admin.ModelAdmin):
    search_fields = ['agile_number']
    list_filter = ['report_type']

class BomBikeAdmin(admin.ModelAdmin):
    ordering = ['model']
    search_fields = ['model']

class BikeReportAdmin(admin.ModelAdmin):
    search_fields = ['pid']

admin.site.register(Part, PartAdmin)
admin.site.register(MfrPartName)
admin.site.register(BomBike, BomBikeAdmin)
admin.site.register(TestReportPart, TestReportPartAdmin)
admin.site.register(TestReportCombo, TestReportComboAdmin)
admin.site.register(BikeReport, BikeReportAdmin)
admin.site.register(SbcProject)