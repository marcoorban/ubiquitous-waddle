from django.contrib import admin
from .models import Machine, LabTestInfo, People, Sample, Test, Bike, Project

@admin.display()
def sample_name(obj):
    return "%s" % (obj.__str__())

@admin.display()
def lims_display(obj):
    return "LIMS-%s" % (obj.lims)

class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_online')

class SampleAdmin(admin.ModelAdmin):
    list_display = [sample_name, 'project']

class TestAdmin(admin.ModelAdmin):
    list_display = ['project', lims_display, 'machine', 'technician', 'labtestinfo']

class LabTestInfoAdmin(admin.ModelAdmin):
    list_display = ['test_full_name', 'test_acronym', 'standard', 'work_instruction']

class BomBikeAdmin(admin.ModelAdmin):
    search_fields = ["model"]

admin.site.register(Machine, MachineAdmin)
admin.site.register(LabTestInfo, LabTestInfoAdmin)
admin.site.register(People)
admin.site.register(Sample, SampleAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Bike)
admin.site.register(Project)


