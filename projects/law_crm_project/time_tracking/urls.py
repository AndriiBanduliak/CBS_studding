"""
URL configuration for time_tracking application.
"""
from django.urls import path
from . import views

app_name = 'time_tracking'

urlpatterns = [
    # Список записей времени
    path('', views.TimeEntryListView.as_view(), name='timeentry_list'),
    path('create/', views.TimeEntryCreateView.as_view(), name='timeentry_create'),
    path('<int:pk>/edit/', views.TimeEntryUpdateView.as_view(), name='timeentry_update'),
    path('<int:pk>/delete/', views.TimeEntryDeleteView.as_view(), name='timeentry_delete'),
    
    # Таймер
    path('timer/', views.TimerView.as_view(), name='timer'),
    path('timer/start/', views.timer_start, name='timer_start'),
    path('timer/pause/', views.timer_pause, name='timer_pause'),
    path('timer/resume/', views.timer_resume, name='timer_resume'),
    path('timer/stop/', views.timer_stop, name='timer_stop'),
    
    # Отчеты
    path('reports/', views.TimeReportView.as_view(), name='time_report'),
]

