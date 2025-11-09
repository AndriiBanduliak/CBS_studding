"""
URL configuration for case_management application.
"""
from django.urls import path
from . import views

app_name = 'case_management'

urlpatterns = [
    # Список и создание дел
    path('', views.CaseListView.as_view(), name='case_list'),
    path('create/', views.CaseCreateView.as_view(), name='case_create'),
    path('<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('<int:pk>/edit/', views.CaseUpdateView.as_view(), name='case_update'),
    path('<int:pk>/delete/', views.CaseDeleteView.as_view(), name='case_delete'),
    
    # События
    path('<int:case_pk>/events/create/', views.CaseEventCreateView.as_view(), 
         name='case_event_create'),
    path('events/<int:pk>/edit/', views.CaseEventUpdateView.as_view(), 
         name='case_event_update'),
    
    # Заметки
    path('<int:case_pk>/notes/create/', views.CaseNoteCreateView.as_view(), 
         name='case_note_create'),
    
    # Ордера
    path('<int:case_pk>/orders/create/', views.LawyerOrderCreateView.as_view(), 
         name='lawyer_order_create'),
    
    # FSM transitions
    path('<int:pk>/transition/<str:transition>/', views.CaseTransitionView.as_view(), 
         name='case_transition'),
]

