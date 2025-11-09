"""
Views для time_tracking приложения.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import TimeEntry, Timer, WorkType
from case_management.models import Case


class TimeEntryListView(LoginRequiredMixin, ListView):
    """Список записей учета времени"""
    model = TimeEntry
    template_name = 'time_tracking/timeentry_list.html'
    context_object_name = 'time_entries'
    paginate_by = 50
    
    def get_queryset(self):
        user = self.request.user
        queryset = TimeEntry.objects.select_related('user', 'case', 'work_type', 'invoice')
        
        # RBAC: адвокат видит только свои записи
        if user.role in ['lawyer', 'assistant']:
            queryset = queryset.filter(user=user)
        # Партнеры и админы видят все
        
        # Фильтры
        case_id = self.request.GET.get('case')
        if case_id:
            queryset = queryset.filter(case_id=case_id)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        is_billed = self.request.GET.get('is_billed')
        if is_billed:
            queryset = queryset.filter(is_billed=(is_billed == 'true'))
        
        return queryset.order_by('-date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика
        queryset = self.get_queryset()
        context['total_hours'] = queryset.aggregate(Sum('duration_hours'))['duration_hours__sum'] or 0
        context['total_amount'] = queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['unbilled_entries'] = queryset.filter(is_billed=False, is_billable=True).count()
        
        return context


class TimeEntryCreateView(LoginRequiredMixin, CreateView):
    """Создание записи учета времени"""
    model = TimeEntry
    template_name = 'time_tracking/timeentry_form.html'
    fields = [
        'case', 'work_type', 'date', 'start_time', 'end_time',
        'duration_hours', 'description', 'hourly_rate', 'is_billable', 'notes'
    ]
    success_url = reverse_lazy('time_tracking:timeentry_list')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = timezone.now().date()
        initial['hourly_rate'] = self.request.user.hourly_rate
        return initial
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Если указаны start_time и end_time, но не duration_hours, рассчитываем
        if form.instance.start_time and form.instance.end_time and not form.instance.duration_hours:
            form.instance.calculate_duration_from_times()
        
        messages.success(self.request, 'Запис обліку часу успішно створено.')
        return super().form_valid(form)


class TimeEntryUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование записи учета времени"""
    model = TimeEntry
    template_name = 'time_tracking/timeentry_form.html'
    fields = [
        'case', 'work_type', 'date', 'start_time', 'end_time',
        'duration_hours', 'description', 'hourly_rate', 'is_billable', 'notes'
    ]
    success_url = reverse_lazy('time_tracking:timeentry_list')
    
    def get_queryset(self):
        # Адвокат может редактировать только свои записи
        qs = super().get_queryset()
        if self.request.user.role in ['lawyer', 'assistant']:
            return qs.filter(user=self.request.user)
        return qs
    
    def form_valid(self, form):
        messages.success(self.request, 'Запис обліку часу успішно оновлено.')
        return super().form_valid(form)


class TimeEntryDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление записи учета времени"""
    model = TimeEntry
    template_name = 'time_tracking/timeentry_confirm_delete.html'
    success_url = reverse_lazy('time_tracking:timeentry_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Запис обліку часу успішно видалено.')
        return super().delete(request, *args, **kwargs)


class TimerView(LoginRequiredMixin, TemplateView):
    """Страница с таймером"""
    template_name = 'time_tracking/timer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Проверяем, есть ли активный таймер у пользователя
        try:
            timer = Timer.objects.get(user=self.request.user)
            context['active_timer'] = timer
            context['elapsed_seconds'] = int(timer.get_elapsed_time().total_seconds())
        except Timer.DoesNotExist:
            context['active_timer'] = None
        
        # Дела для выбора
        user = self.request.user
        if user.role in ['partner', 'admin']:
            context['cases'] = Case.objects.filter(status='in_progress')
        else:
            context['cases'] = Case.objects.filter(
                lawyers=user, status='in_progress'
            )
        
        context['work_types'] = WorkType.objects.filter(is_active=True)
        
        return context


@login_required
def timer_start(request):
    """Запуск таймера"""
    if request.method == 'POST':
        case_id = request.POST.get('case_id')
        work_type_id = request.POST.get('work_type_id')
        description = request.POST.get('description', '')
        
        # Проверяем, нет ли уже активного таймера
        if Timer.objects.filter(user=request.user).exists():
            return JsonResponse({
                'success': False,
                'error': 'У вас вже є активний таймер. Зупиніть його перед запуском нового.'
            })
        
        try:
            case = Case.objects.get(id=case_id)
            work_type = WorkType.objects.get(id=work_type_id)
            
            timer = Timer.objects.create(
                user=request.user,
                case=case,
                work_type=work_type,
                description=description
            )
            
            return JsonResponse({
                'success': True,
                'timer_id': timer.id,
                'message': 'Таймер запущено'
            })
        except (Case.DoesNotExist, WorkType.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'error': 'Невірні дані'
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def timer_pause(request):
    """Пауза таймера"""
    if request.method == 'POST':
        try:
            timer = Timer.objects.get(user=request.user)
            timer.is_paused = True
            timer.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Таймер призупинено'
            })
        except Timer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Активний таймер не знайдено'
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def timer_resume(request):
    """Возобновление таймера"""
    if request.method == 'POST':
        try:
            timer = Timer.objects.get(user=request.user)
            timer.is_paused = False
            timer.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Таймер відновлено'
            })
        except Timer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Активний таймер не знайдено'
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def timer_stop(request):
    """Остановка таймера и создание записи учета времени"""
    if request.method == 'POST':
        try:
            timer = Timer.objects.get(user=request.user)
            description = request.POST.get('description', timer.description)
            timer.description = description
            
            time_entry = timer.stop_and_create_entry()
            
            return JsonResponse({
                'success': True,
                'message': 'Таймер зупинено. Створено запис обліку часу.',
                'time_entry_id': time_entry.id,
                'duration_hours': float(time_entry.duration_hours),
                'total_amount': float(time_entry.total_amount)
            })
        except Timer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Активний таймер не знайдено'
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


class TimeReportView(LoginRequiredMixin, TemplateView):
    """Отчеты по учету времени"""
    template_name = 'time_tracking/time_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Период для отчета (по умолчанию - текущий месяц)
        today = timezone.now().date()
        date_from = self.request.GET.get('date_from', today.replace(day=1))
        date_to = self.request.GET.get('date_to', today)
        
        # Базовый queryset
        queryset = TimeEntry.objects.filter(date__gte=date_from, date__lte=date_to)
        
        if user.role in ['lawyer', 'assistant']:
            queryset = queryset.filter(user=user)
        
        # Статистика
        context['total_hours'] = queryset.aggregate(Sum('duration_hours'))['duration_hours__sum'] or 0
        context['total_amount'] = queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['billable_hours'] = queryset.filter(is_billable=True).aggregate(
            Sum('duration_hours')
        )['duration_hours__sum'] or 0
        context['billed_amount'] = queryset.filter(is_billed=True).aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
        
        # Группировка по делам
        context['by_case'] = queryset.values(
            'case__case_number', 'case__title'
        ).annotate(
            total_hours=Sum('duration_hours'),
            total_amount=Sum('total_amount')
        ).order_by('-total_hours')
        
        # Группировка по типам работ
        context['by_work_type'] = queryset.values(
            'work_type__name'
        ).annotate(
            total_hours=Sum('duration_hours'),
            total_amount=Sum('total_amount')
        ).order_by('-total_hours')
        
        context['date_from'] = date_from
        context['date_to'] = date_to
        
        return context

