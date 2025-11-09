from django.urls import path
from . import views

urlpatterns = [
    path('occupancy/', views.occupancy_report),
    path('bookings.csv', views.bookings_csv_export),
]


