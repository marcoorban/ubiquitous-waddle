from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe
from calendar import monthrange

from .models import People, Machine, Test
from .utils import Calendar, WeeklyCalendar
from .forms import TestForm, EditTestForm, TEST_RESULTS

# Create your views here.

def index(request):
    return render(request, 'test_lab_schedule/index.html')

class TestView(generic.DetailView):
    model = Test
    template_name = 'test_lab_schedule/test.html'

class CalendarView(generic.ListView):
    model = Test
    template_name = 'test_lab_schedule/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month',None))
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['header'] = 'Calendar'
        return context

def weekview(request, filter='machine'):
    template_name = 'test_lab_schedule/week.html'

    # use today's date for the calendar
    d = get_date(request.GET.get('week',None))

    # Instantiate our calendar class with today's year and date
    cal = WeeklyCalendar(d.year, d.month, d.day)

    # Get the dates for today's week in the calendar
    dates = cal.get_week()[1]

    return render(request, 'test_lab_schedule/week.html', {
        'prev_week':prev_week(d),
        'next_week':next_week(d),
        'today':this_week(d),
        'filter':filter,
        'dates':dates,
        'rows':[],
        'header':filter.capitalize()
    })

def test_list(request, filter):
    d = get_date(request.GET.get('week',None))
    cal = WeeklyCalendar(d.year, d.month, d.day)
    tests = cal.get_tests(filter)
    return render(request, "test_lab_schedule/test_list.html", {"tests":tests, 'filter':filter})

def add_test(request):
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            lims = form.cleaned_data['lims']
            labtestinfo = form.cleaned_data['labtestinfo']
            machine = form.cleaned_data['machine']
            technician = form.cleaned_data['technician']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            test = Test.objects.create(
                lims=lims,
                labtestinfo=labtestinfo,
                start_date=start_date,
                end_date=end_date,
                machine=machine,
                technician=technician
            )
            test.save()
            return HttpResponse(status=204, headers={'HX-Trigger':"testListChanged"}) # 204 is status code for no content
    else:
        form = TestForm()
    return render(request, 'test_lab_schedule/test_form.html', {
        'form':form,
        'add_or_edit':'Add',
    })

def add_test_navbar(request):
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            lims = form.cleaned_data['lims']
            labtestinfo = form.cleaned_data['labtestinfo']
            machine = form.cleaned_data['machine']
            technician = form.cleaned_data['technician']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            test = Test.objects.create(
                lims=lims,
                labtestinfo=labtestinfo,
                start_date=start_date,
                end_date=end_date,
                machine=machine,
                technician=technician
            )
            test.save()
            return redirect("test_lab_schedule:week")
    else:
        form = TestForm()
    return render(request, 'test_lab_schedule/test_form_navbar.html', {
        'form':form,
        'add_or_edit':'Add',
    })

def edit_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == "POST":
        form = EditTestForm(request.POST)
        if form.is_valid():
            test.machine = form.cleaned_data['machine']
            test.technician = form.cleaned_data['technician']
            test.start_date = form.cleaned_data['start_date']
            test.end_date = form.cleaned_data['end_date']
            test.result = form.cleaned_data['result']
            test.save()
            return HttpResponse(status=204, headers={'HX-Trigger':"testListChanged"}) # 204 is status code for no content
    else:
        form = EditTestForm(data={
            'machine':test.machine,
            'technician':test.technician,
            'start_date':test.start_date,
            'end_date':test.end_date,
            'result':test.result
        })
    return render(request, 'test_lab_schedule/edit_test_form.html', {
        'form':form,
        'test':test,
        'add_or_edit':'Edit'
    })

def addSample(request):
    return render(request, 'test_lab_schdule/add_sample.html')

def get_date(req_day):
    if req_day and len(req_day.split('-'))==3:
        year, month, day = (int(x) for x in req_day.split('-'))
        return date(year, month, day)
    elif req_day and len(req_day.split('-'))==2:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, 1)
    return date.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def prev_week(today):
    date_one_week_ago = today - timedelta(days=7)
    week = 'week=' + str(date_one_week_ago.year) + '-' + str(date_one_week_ago.month) + '-' + str(date_one_week_ago.day)
    return week

def next_week(today):
    date_one_week_later = today + timedelta(days=7)
    week = 'week=' + str(date_one_week_later.year) + '-' + str(date_one_week_later.month) + '-' + str(date_one_week_later.day)
    return week

def this_week(today):
    week = 'week=' + str(today.year) + '-' + str(today.month) + '-' + str(today.day)
    return week