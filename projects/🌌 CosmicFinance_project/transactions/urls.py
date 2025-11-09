from django.urls import path
from .views import (
    CategoryListCreateView,
    TransactionListCreateView,
    TransactionDetailView,
    MonthlySummaryView,
    CategorySummaryView,
    DeleteAllDataView,
)

urlpatterns = [
    # Category endpoints
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    
    # Transaction endpoints
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    
    # Analytics endpoints
    path('stats/monthly_summary/', MonthlySummaryView.as_view(), name='monthly-summary'),
    path('stats/category_summary/', CategorySummaryView.as_view(), name='category-summary'),
    
    # Data management
    path('delete-all/', DeleteAllDataView.as_view(), name='delete-all-data'),
]

