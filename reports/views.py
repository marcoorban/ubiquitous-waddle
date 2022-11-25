from datetime import date

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView

from .models import BikeReport, BomBike, Part, TestReportCombo, TestReportPart
from .importers import Csv_Importer
from .forms import CsvUploadForm, BikeSearchForm

# Create your views here.
def home(request):
    return render(request, 'reports/home.html')

class BomBikeView(ListView):
    this_year = date.today().year
    next_year = this_year + 1
    families = []
    bikes = []

    model = BomBike
    # Obtain the bikes for this calendar year (from Jan 1 to Dec 31)
    queryset = BomBike.objects.filter(production_date__gte=str(this_year)+'-01-01').filter(production_date__lt=str(next_year)+'-01-01').order_by('production_date')
    for bike in queryset:
        if bike.model not in families:
            bikes.append(bike)
            families.append(bike.model)
    queryset = bikes
    context_object_name = 'bikes'
    template_name = 'reports/bike_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the parts

        return context

class PartListView(ListView):
    template_name = 'reports/part_list.html'

class PartDetailView(DetailView):
    model = Part
    # generic views uses template name <app name>/<model name>_detail.html
    template_name = 'reports/part_detail.html'

class TrpDetailView(DetailView):
    model = TestReportPart
    template_name = 'reports/trp_detail.html'

class TrcDetailView(DetailView):
    model = TestReportCombo
    template_name = 'reports/trc_detail.html'

def bikereport(request, pid):
    bikereport = BikeReport.objects.get(pid=pid)
    bikes = BomBike.objects.filter(report=bikereport)
    return render(request, 'reports/bike_report.html', {
        'bikes':bikes, 
        'bikereport':bikereport, 
        }
    )

def bike_search(request):
    if request.method == "POST":
        form = BikeSearchForm(request.POST)
        if form.is_valid():
            model_year = form.cleaned_data['model_year']
            search_term = form.cleaned_data['search']
            if model_year:
                results = BikeReport.objects.filter(description__contains=model_year).filter(description__contains=search_term)
            else:
                results = BikeReport.objects.filter(description__contains=search_term)

            form = BikeSearchForm()
            return render(request, 'reports/bike_search.html', {'form':form, 'results':results})
    else:
        form = BikeSearchForm()
    
    return render(request, 'reports/bike_search.html', {'form':form})

def part_search(request):
    if request.method == "POST":
        parts = Part.objects.filter(description__contains = request.POST['description'])
        if not parts:
            # Redisplay the form
            return render(request, 'reports/part_search.html', {
                'error_message': "Could not find part."
            })
        else:
            # Always return an HttpResponseRedirect after succesfully dealing with POST data.
            # This prevents data from being posted twice if a user hits the Back button.
            return render(request, 'reports/part_search.html', {'parts':parts})
    else:
        return render(request, 'reports/part_search.html')

def csv_upload(request):

    if request.method == "POST":
        form = CsvUploadForm(request.POST, request.FILES)
        # Form is already checking that the uploaded file is csv. Refer
        # to validators argument in the FileField of csv upload form in forms.py
        if form.is_valid():
            importer = Csv_Importer(request.FILES['attachment'])
            # Read the file and get the headers
            try:
                importer.read_file()
            except:
                return HttpResponseRedirect(reverse('reports:failure'))
            # Determine if it's a part, trp, trc, etc.
            importer.determine_type()
            if importer.csv_type == "unknown":
                return HttpResponseRedirect(reverse('reports:failure'))
            # Import the data
            importer.import_all()
            return render(request, 'reports/csv_upload.html')
        else:
            return HttpResponseRedirect(reverse('reports:failure'))
    else:
        form = CsvUploadForm()
    return render(request, 'reports/csv_upload.html')

def failure(request):
    return render(request, 'reports/failure.html')

def success(request):
    return render(request, 'reports/success.html')

def bike_readiness(request):
    # get the current year
    next_year = date.today().year + 1

    # Processing the form data for a POST request
    if request.method == "POST":
        # create a form instance and populate it with data from the request
        form = BikeSearchForm(request.POST)
        date1 = date(year=next_year, month=1, day=1)
        date2 = date(year=next_year, month=12, day=31)
        bikes = []
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            bike_model = form.cleaned_data['bike_model']
            production_year = form.cleaned_data['production_year']
            quarter = form.cleaned_data['quarter']
            
            if production_year and quarter:
                date1 = date(year=production_year, month=int(quarter.split("-")[0]), day=1)
                date2 = date(year=production_year, month=int(quarter.split("-")[1]), day=1)

            elif production_year:
                date1 = date(year=production_year, month=1, day=1)
                date2 = date(year=production_year, month=12, day=1)

            if bike_model:
                bikes = BomBike.objects.filter(
                    model__icontains=bike_model).filter(
                        production_date__gte=date1).filter(production_date__lte=date2).order_by(
                            'production_date'
                        )
            else:
                bikes = BomBike.objects.filter(
                        production_date__gte=date1).filter(production_date__lte=date2).order_by(
                            'production_date'
                        )

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BikeSearchForm()
        bikes = []
    
    return render(request, 'reports/bike_readiness.html',
            {
                "bikes":bikes,
                "form":form
            }
        )
