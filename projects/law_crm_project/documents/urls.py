"""
URL configuration for documents application.
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Документы
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
    
    # Шаблоны
    path('templates/', views.DocumentTemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/generate/', views.generate_from_template, name='template_generate'),
    
    # Поиск
    path('search/', views.DocumentSearchView.as_view(), name='document_search'),
]

