"""
Views для case_management приложения.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.db.models import Q, Prefetch
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .models import Case, CaseEvent, CaseNote, LawyerOrder, Court
from core.models import Client, User


class CaseListView(LoginRequiredMixin, ListView):
    """Список дел"""
    model = Case
    template_name = 'case_management/case_list.html'
    context_object_name = 'cases'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = Case.objects.select_related(
            'client', 'court', 'responsible_lawyer'
        ).prefetch_related('lawyers')
        
        # RBAC: фильтрация по правам доступа
        if user.role == 'lawyer':
            queryset = queryset.filter(lawyers=user)
        elif user.role == 'assistant':
            queryset = queryset.filter(assistants=user)
        # partner и admin видят все дела
        
        # Фильтры
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        proceeding_type = self.request.GET.get('proceeding_type')
        if proceeding_type:
            queryset = queryset.filter(proceeding_type=proceeding_type)
        
        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(case_number__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(client__first_name__icontains=search_query) |
                Q(client__last_name__icontains=search_query) |
                Q(client__company_name__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')


class CaseDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о деле"""
    model = Case
    template_name = 'case_management/case_detail.html'
    context_object_name = 'case'
    
    def get_queryset(self):
        return Case.objects.select_related(
            'client', 'court', 'responsible_lawyer', 'created_by'
        ).prefetch_related(
            'lawyers', 'assistants', 'orders', 'events', 'case_notes__author'
        )
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Проверка доступа
        if not request.user.can_access_case(self.object):
            return HttpResponseForbidden("У вас немає доступу до цієї справи.")
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case = self.object
        
        # События (ближайшие)
        context['upcoming_events'] = case.events.filter(
            is_completed=False
        ).order_by('event_date')[:5]
        
        # Последние заметки
        context['recent_notes'] = case.case_notes.select_related('author')[:5]
        
        # Ордера
        context['orders'] = case.orders.filter(is_active=True)
        
        return context


class CaseCreateView(LoginRequiredMixin, CreateView):
    """Создание нового дела"""
    model = Case
    template_name = 'case_management/case_form.html'
    fields = [
        'case_number', 'title', 'description', 'proceeding_type',
        'client', 'opposing_party', 'opposing_party_lawyer',
        'court', 'judge', 'responsible_lawyer',
        'registration_date', 'first_hearing_date', 'next_hearing_date',
        'deadline_date', 'estimated_value', 'contract_amount',
        'notes', 'is_priority'
    ]
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Справу успішно створено.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('case_management:case_detail', kwargs={'pk': self.object.pk})


class CaseUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование дела"""
    model = Case
    template_name = 'case_management/case_form.html'
    fields = [
        'case_number', 'title', 'description', 'proceeding_type',
        'client', 'opposing_party', 'opposing_party_lawyer',
        'court', 'judge', 'responsible_lawyer',
        'registration_date', 'first_hearing_date', 'next_hearing_date',
        'deadline_date', 'estimated_value', 'contract_amount',
        'notes', 'is_priority', 'egrsr_id'
    ]
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.can_access_case(self.object):
            return HttpResponseForbidden("У вас немає доступу до цієї справи.")
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Дані справи успішно оновлено.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('case_management:case_detail', kwargs={'pk': self.object.pk})


class CaseDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление дела"""
    model = Case
    template_name = 'case_management/case_confirm_delete.html'
    success_url = reverse_lazy('case_management:case_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Справу успішно видалено.')
        return super().delete(request, *args, **kwargs)


class CaseEventCreateView(LoginRequiredMixin, CreateView):
    """Создание события по делу"""
    model = CaseEvent
    template_name = 'case_management/case_event_form.html'
    fields = ['event_type', 'title', 'description', 'event_date', 'location']
    
    def form_valid(self, form):
        case_pk = self.kwargs['case_pk']
        form.instance.case_id = case_pk
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Подію успішно створено.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('case_management:case_detail', 
                          kwargs={'pk': self.kwargs['case_pk']})


class CaseEventUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование события"""
    model = CaseEvent
    template_name = 'case_management/case_event_form.html'
    fields = ['event_type', 'title', 'description', 'event_date', 
              'location', 'is_completed', 'result']
    
    def get_success_url(self):
        return reverse_lazy('case_management:case_detail', 
                          kwargs={'pk': self.object.case.pk})


class CaseNoteCreateView(LoginRequiredMixin, CreateView):
    """Создание заметки по делу"""
    model = CaseNote
    template_name = 'case_management/case_note_form.html'
    fields = ['content', 'is_important']
    
    def form_valid(self, form):
        case_pk = self.kwargs['case_pk']
        form.instance.case_id = case_pk
        form.instance.author = self.request.user
        messages.success(self.request, 'Нотатку успішно створено.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('case_management:case_detail', 
                          kwargs={'pk': self.kwargs['case_pk']})


class LawyerOrderCreateView(LoginRequiredMixin, CreateView):
    """Создание ордера"""
    model = LawyerOrder
    template_name = 'case_management/lawyer_order_form.html'
    fields = ['lawyer', 'order_series', 'order_number', 'issue_date', 'issued_by', 'notes']
    
    def form_valid(self, form):
        case_pk = self.kwargs['case_pk']
        form.instance.case_id = case_pk
        messages.success(self.request, 'Ордер успішно створено.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('case_management:case_detail', 
                          kwargs={'pk': self.kwargs['case_pk']})


class CaseTransitionView(LoginRequiredMixin, View):
    """Изменение статуса дела (FSM transition)"""
    
    def post(self, request, pk, transition):
        case = get_object_or_404(Case, pk=pk)
        
        # Проверка доступа
        if not request.user.can_access_case(case):
            return HttpResponseForbidden("У вас немає доступу до цієї справи.")
        
        # Выполнение перехода
        try:
            transition_method = getattr(case, transition)
            transition_method()
            case.save()
            messages.success(request, f'Статус справи змінено на "{case.get_status_display()}".')
        except Exception as e:
            messages.error(request, f'Помилка зміни статусу: {str(e)}')
        
        return redirect('case_management:case_detail', pk=pk)

