"""
Views для documents приложения.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.contrib.postgres.search import SearchQuery, SearchRank
from .models import Document, DocumentTemplate, DocumentCategory
from case_management.models import Case


class DocumentListView(LoginRequiredMixin, ListView):
    """Список документов"""
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Document.objects.select_related(
            'case', 'category', 'uploaded_by'
        )
        
        # Фильтр по делу
        case_id = self.request.GET.get('case')
        if case_id:
            queryset = queryset.filter(case_id=case_id)
        
        # Фильтр по типу
        document_type = self.request.GET.get('type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(registration_number__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')


class DocumentDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о документе"""
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'


class DocumentCreateView(LoginRequiredMixin, CreateView):
    """Создание документа"""
    model = Document
    template_name = 'documents/document_form.html'
    fields = [
        'case', 'category', 'document_type', 'title', 'description',
        'file', 'document_date', 'author_name', 'recipient_name',
        'registration_number', 'is_confidential'
    ]
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Документ успішно завантажено.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('documents:document_detail', kwargs={'pk': self.object.pk})


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование документа"""
    model = Document
    template_name = 'documents/document_form.html'
    fields = [
        'case', 'category', 'document_type', 'title', 'description',
        'document_date', 'author_name', 'recipient_name',
        'registration_number', 'is_confidential'
    ]
    
    def get_success_url(self):
        return reverse_lazy('documents:document_detail', kwargs={'pk': self.object.pk})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление документа"""
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('documents:document_list')


@login_required
def document_download(request, pk):
    """Скачивание документа"""
    document = get_object_or_404(Document, pk=pk)
    
    # Проверка доступа (если документ привязан к делу)
    if document.case and not request.user.can_access_case(document.case):
        raise Http404("Документ не знайдено")
    
    try:
        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )
    except FileNotFoundError:
        raise Http404("Файл не знайдено")


class DocumentTemplateListView(LoginRequiredMixin, ListView):
    """Список шаблонов документов"""
    model = DocumentTemplate
    template_name = 'documents/template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        return DocumentTemplate.objects.filter(is_active=True)


@login_required
def generate_from_template(request, pk):
    """Генерация документа из шаблона"""
    template = get_object_or_404(DocumentTemplate, pk=pk)
    
    if request.method == 'POST':
        case_id = request.POST.get('case_id')
        case = get_object_or_404(Case, pk=case_id)
        
        # Подготовка контекста для генерации
        context_data = {
            'case_number': case.case_number,
            'case_title': case.title,
            'client_name': case.client.full_name,
            'client_address': case.client.address,
            'client_identifier': case.client.identifier,
            'court_name': case.court.name if case.court else '',
            'opposing_party': case.opposing_party,
            'today_date': request.user.timezone.now().strftime('%d.%m.%Y'),
            'lawyer_name': request.user.get_full_name(),
            'lawyer_certificate': request.user.naau_certificate_number or '',
        }
        
        # Генерация документа
        try:
            generated_file = template.generate_document(context_data)
            
            # Создание записи о документе
            document = Document.objects.create(
                case=case,
                document_type=template.document_type,
                title=f"{template.name} - {case.case_number}",
                description=f"Згенеровано з шаблону '{template.name}'",
                uploaded_by=request.user,
                is_confidential=True
            )
            
            # Сохранение файла
            from django.core.files.base import ContentFile
            document.file.save(
                f"generated_{template.name}_{case.case_number}.docx",
                ContentFile(generated_file.read())
            )
            
            messages.success(request, 'Документ успішно згенеровано.')
            return redirect('documents:document_detail', pk=document.pk)
        
        except Exception as e:
            messages.error(request, f'Помилка генерації документу: {str(e)}')
            return redirect('documents:template_list')
    
    # GET запрос - показываем форму
    context = {
        'template': template,
        'cases': Case.objects.filter(status='in_progress')
    }
    return render(request, 'documents/template_generate.html', context)


class DocumentSearchView(LoginRequiredMixin, ListView):
    """
    Полнотекстовый поиск документов с использованием PostgreSQL Full-Text Search.
    """
    model = Document
    template_name = 'documents/document_search.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        query_text = self.request.GET.get('q', '')
        
        if not query_text:
            return Document.objects.none()
        
        # PostgreSQL Full-Text Search
        search_query = SearchQuery(query_text, config='simple')
        
        queryset = Document.objects.annotate(
            rank=SearchRank('search_vector', search_query)
        ).filter(
            search_vector=search_query
        ).order_by('-rank')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

