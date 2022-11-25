from datetime import datetime
from calendar import HTMLCalendar
from django.urls import reverse
from .models import Machine, Test

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, tests):
        tests_per_day = tests.filter(end_date__day__gte=day).filter(start_date__day__lte=day)
        d = ''
        for test in tests_per_day:
            url = reverse('test_lab_schedule:test', args=(test.id,))
            d += f"<a href='{url}'><li class='calendar-li'>[{test.machine}] {test.labtestinfo} LIMS-{test.lims}</li>"

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, tests):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, tests)
        return f'<tr scope="col"> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        tests = Test.objects.filter(start_date__year=self.year, start_date__month=self.month)
        cal = f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, tests)}\n'
        return cal

class WeeklyCalendar(Calendar):
    def __init__(self, year=None, month=None, day=None):
        self.year = year
        self.month = month
        self.day = day
        self.dates = {}
        super(Calendar, self).__init__()

    def get_week(self):
        weeks = self.monthdays2calendar(self.year, self.month)
        if not self.day:
            self.day = datetime.today().day
        for week in weeks:
            for daytuple in week:
                if self.day == daytuple[0]:
                    this_week = weeks[weeks.index(week)]
                    try:
                        next_week = weeks[weeks.index(week)+1]
                    # If next week is the last week of the month, try the next month instead
                    except IndexError:
                        try:
                            next_week = self.monthdays2calendar(self.year, self.month+1)[0]
                        # If next week is the last week of Decemeber, try January of next year
                        except self.IllegalMonthError:
                            next_week = self.monthdays2calendar(self.year+1, 1)[0]

                    dates = {
                        'Mon':this_week[0][0],
                        'Tue':this_week[1][0],
                        'Wed':this_week[2][0],
                        'Thu':this_week[3][0],
                        'Fri':this_week[4][0],
                    }
        return this_week, dates

    def get_machine_daily_tests(self, day, machine):
        tests = Test.objects.filter(machine=machine).filter(end_date__day__gte=day).filter(start_date__day__lte=day)
        return tests

    def get_weekly_tests(self, theweek, objectt):
        week = []
        if isinstance(objectt, Machine):
            machine = objectt
            for d, weekday in theweek[0:5]:
                week.append(self.get_machine_daily_tests(d, machine))
        return week

    def get_tests(self, filter, withyear=True):
        if filter == 'machine':
            objects = Machine.objects.all()
        # Get the days of the current or desired week
        week=self.get_week()[0]
        tests = []
        for objectt in objects:
            week_items = self.get_weekly_tests(week, objectt)
            tests.append({
                'object':objectt,
                'tests':week_items
            })

        return tests

