from django.urls import path

from . import views

app_name = 'reports'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('bike_list/', views.BomBikeView.as_view(), name='bike_list'),
    path('bike_report/<int:pid>/', views.bikereport, name='bikereport'),
    path('part_list/', views.PartListView.as_view(), name='part_view'),
    path('testreportpart/<int:pk>/', views.TrpDetailView.as_view(), name='trp_detail'),
    path('testreportcombo/<int:pk>/', views.TrcDetailView.as_view(), name='trc_detail'),
    path('part/<int:pk>/', views.PartDetailView.as_view(), name='part_detail'),
    path('part_search/', views.part_search, name='part_search'),
    path('bike_search/', views.bike_search, name='bike_search'),
    path('csv_upload/', views.csv_upload, name='csv_upload'),
    path('failure/', views.failure, name='failure'),
    path('readiness/', views.bike_readiness, name='bike_readiness'),
]