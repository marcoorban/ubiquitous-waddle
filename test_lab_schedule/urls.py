from django.urls import path, re_path
from django.contrib import admin

from . import views

app_name = 'test_lab_schedule'
urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls, name='admin'),
    path('test/add/', views.add_test, name='add_test'),
    path('test/add/navbar', views.add_test_navbar, name='add_test_navbar'),
    path('test/edit/', views.edit_test, name='edit_test'),
    re_path(r'^test/edit/(?P<pk>\w+)/$', views.edit_test),
    path('test/<int:pk>', views.TestView.as_view(), name='test'),
    path('add_sample', views.addSample, name='add_sample'),
    path('test/<int:pk>/edit', views.edit_test, name='edit_test'),
    re_path(r'^calendar/$', views.CalendarView.as_view(), name='calendar'),
    path('week/', views.weekview, name='week'),
    re_path(r'^week/(?P<filter>\w+)/$', views.weekview, name='filterweek'),
    path('tests/', views.test_list, name='test_list'),
    re_path(r'^tests/(?P<filter>\w+)/$', views.test_list, name='filtertestlist')
]