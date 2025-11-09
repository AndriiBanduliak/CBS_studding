"""
Views для core приложения.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib import messages
from .models import Client, ConflictCheck, User
from case_management.models import Case


class DashboardView(LoginRequiredMixin, TemplateView):
    """Главная страница (Dashboard)"""
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Статистика для дашборда
        if user.role in ['partner', 'admin']:
            # Партнеры и администраторы видят все
            cases_qs = Case.objects.all()
            clients_count = Client.objects.filter(is_active=True).count()
        else:
            # Адвокаты видят только свои дела
            cases_qs = Case.objects.filter(lawyers=user)
            clients_count = Client.objects.filter(
                responsible_lawyer=user, is_active=True
            ).count()
        
        context.update({
            'total_cases': cases_qs.count(),
            'active_cases': cases_qs.filter(status='in_progress').count(),
            'clients_count': clients_count,
            'recent_cases': cases_qs.order_by('-created_at')[:5],
        })
        
        return context


class ClientListView(LoginRequiredMixin, ListView):
    """Список клиентов"""
    model = Client
    template_name = 'core/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Client.objects.select_related('responsible_lawyer')
        
        # Фильтрация по типу клиента
        client_type = self.request.GET.get('type')
        if client_type:
            queryset = queryset.filter(client_type=client_type)
        
        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(company_name__icontains=search_query) |
                Q(rnokpp__icontains=search_query) |
                Q(edrpou__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        return queryset


class ClientDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о клиенте"""
    model = Client
    template_name = 'core/client_detail.html'
    context_object_name = 'client'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object
        
        # Получаем все дела клиента
        context['cases'] = client.cases.select_related('court').prefetch_related('lawyers')
        
        # Проверки конфликта интересов
        context['conflict_checks'] = client.conflict_checks.select_related('checked_by')
        
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создание нового клиента"""
    model = Client
    template_name = 'core/client_form.html'
    fields = [
        'client_type', 'first_name', 'last_name', 'middle_name',
        'company_name', 'rnokpp', 'edrpou', 'email', 'phone',
        'phone_additional', 'address', 'passport_data',
        'representative_name', 'representative_position',
        'responsible_lawyer', 'notes'
    ]
    success_url = reverse_lazy('core:client_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Клієнта успішно створено.')
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование клиента"""
    model = Client
    template_name = 'core/client_form.html'
    fields = [
        'client_type', 'first_name', 'last_name', 'middle_name',
        'company_name', 'rnokpp', 'edrpou', 'email', 'phone',
        'phone_additional', 'address', 'passport_data',
        'representative_name', 'representative_position',
        'responsible_lawyer', 'notes', 'is_active'
    ]
    
    def get_success_url(self):
        return reverse_lazy('core:client_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Дані клієнта успішно оновлено.')
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление клиента"""
    model = Client
    template_name = 'core/client_confirm_delete.html'
    success_url = reverse_lazy('core:client_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Клієнта успішно видалено.')
        return super().delete(request, *args, **kwargs)


class ConflictCheckCreateView(LoginRequiredMixin, CreateView):
    """Создание проверки конфликта интересов"""
    model = ConflictCheck
    template_name = 'core/conflict_check_form.html'
    fields = ['opposing_party_name', 'opposing_party_identifier', 
              'has_conflict', 'conflict_details']
    
    def form_valid(self, form):
        client_pk = self.kwargs['client_pk']
        form.instance.client_id = client_pk
        form.instance.checked_by = self.request.user
        
        # Автоматическая проверка конфликта
        opposing_identifier = form.instance.opposing_party_identifier
        if opposing_identifier:
            # Проверяем, не является ли противоположная сторона нашим клиентом
            conflict_exists = Client.objects.filter(
                Q(rnokpp=opposing_identifier) | Q(edrpou=opposing_identifier)
            ).exists()
            
            if conflict_exists:
                form.instance.has_conflict = True
                if not form.instance.conflict_details:
                    form.instance.conflict_details = 'Протилежна сторона є клієнтом об\'єднання'
        
        messages.success(self.request, 'Перевірку конфлікту інтересів виконано.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:client_detail', kwargs={'pk': self.kwargs['client_pk']})


class SearchView(LoginRequiredMixin, TemplateView):
    """Глобальный поиск по системе"""
    template_name = 'core/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        if query:
            # Поиск клиентов
            context['clients'] = Client.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(company_name__icontains=query) |
                Q(rnokpp__icontains=query) |
                Q(edrpou__icontains=query)
            )[:10]
            
            # Поиск дел
            context['cases'] = Case.objects.filter(
                Q(case_number__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )[:10]
        
        context['query'] = query
        return context

