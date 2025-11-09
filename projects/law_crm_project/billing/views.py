"""
Views для billing приложения.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Invoice, InvoiceItem, Payment
from case_management.models import Case


class InvoiceListView(LoginRequiredMixin, ListView):
    """Список счетов"""
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Invoice.objects.select_related('case', 'client', 'created_by')
        
        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-issue_date')


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о счете"""
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        return Invoice.objects.select_related(
            'case', 'client', 'created_by'
        ).prefetch_related('items', 'payments', 'time_entries')


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    """Создание счета"""
    model = Invoice
    template_name = 'billing/invoice_form.html'
    fields = [
        'invoice_number', 'case', 'client', 'issue_date', 'due_date',
        'subtotal', 'tax_rate', 'description', 'notes',
        'lawyer_name', 'lawyer_certificate', 'lawyer_bank_account'
    ]
    
    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        
        # Предзаполнение данных адвоката
        initial['lawyer_name'] = user.get_full_name()
        initial['lawyer_certificate'] = user.naau_certificate_number
        initial['lawyer_bank_account'] = user.bank_account
        
        # Если указано дело, предзаполняем клиента
        case_id = self.request.GET.get('case')
        if case_id:
            try:
                case = Case.objects.get(id=case_id)
                initial['case'] = case
                initial['client'] = case.client
            except Case.DoesNotExist:
                pass
        
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Рахунок успішно створено.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('billing:invoice_detail', kwargs={'pk': self.object.pk})


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование счета"""
    model = Invoice
    template_name = 'billing/invoice_form.html'
    fields = [
        'invoice_number', 'case', 'client', 'status', 'issue_date', 'due_date',
        'subtotal', 'tax_rate', 'description', 'notes',
        'lawyer_name', 'lawyer_certificate', 'lawyer_bank_account'
    ]
    
    def get_success_url(self):
        return reverse_lazy('billing:invoice_detail', kwargs={'pk': self.object.pk})


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление счета"""
    model = Invoice
    template_name = 'billing/invoice_confirm_delete.html'
    success_url = reverse_lazy('billing:invoice_list')


@login_required
def invoice_generate_pdf(request, pk):
    """
    Генерация PDF счета.
    Использует ReportLab для создания PDF на украинском языке.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Создание PDF в памяти
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    # Элементы документа
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Заголовок
    elements.append(Paragraph(
        f"РАХУНОК № {invoice.invoice_number}<br/>від {invoice.issue_date.strftime('%d.%m.%Y')}",
        title_style
    ))
    elements.append(Spacer(1, 1*cm))
    
    # Информация о клиенте и адвокате
    info_data = [
        ['Виконавець:', invoice.lawyer_name],
        ['Свідоцтво:', invoice.lawyer_certificate or '-'],
        ['Банківський рахунок:', invoice.lawyer_bank_account or '-'],
        ['', ''],
        ['Замовник:', invoice.client.full_name],
        ['Ідентифікатор:', invoice.client.identifier or '-'],
        ['Адреса:', invoice.client.address or '-'],
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 1*cm))
    
    # Описание услуг
    elements.append(Paragraph('<b>Надані послуги:</b>', styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(invoice.description or 'Юридичні послуги', styles['Normal']))
    elements.append(Spacer(1, 1*cm))
    
    # Таблица с суммами
    amounts_data = [
        ['Опис', 'Сума'],
        ['Вартість послуг', f"{invoice.subtotal:.2f} грн"],
        [f'ПДВ ({invoice.tax_rate}%)', f"{invoice.tax_amount:.2f} грн"],
        ['ВСЬОГО до сплати:', f"{invoice.total:.2f} грн"],
    ]
    
    amounts_table = Table(amounts_data, colWidths=[14*cm, 3*cm])
    amounts_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BOX', (0, -1), (-1, -1), 2, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(amounts_table)
    
    # Строим PDF
    doc.build(elements)
    
    # Возвращаем PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    
    return response


@login_required
def invoice_mark_paid(request, pk):
    """Отметить счет как оплаченный"""
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, pk=pk)
        paid_date = request.POST.get('paid_date', timezone.now().date())
        
        invoice.mark_as_paid(paid_date)
        messages.success(request, 'Рахунок відмічено як оплачений.')
        
        return redirect('billing:invoice_detail', pk=pk)
    
    return redirect('billing:invoice_list')


class PaymentListView(LoginRequiredMixin, ListView):
    """Список платежей"""
    model = Payment
    template_name = 'billing/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        return Payment.objects.select_related('invoice', 'received_by').order_by('-payment_date')


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """Регистрация платежа"""
    model = Payment
    template_name = 'billing/payment_form.html'
    fields = ['invoice', 'amount', 'payment_date', 'payment_method', 'reference_number', 'notes']
    success_url = reverse_lazy('billing:payment_list')
    
    def form_valid(self, form):
        form.instance.received_by = self.request.user
        messages.success(self.request, 'Платіж успішно зареєстровано.')
        return super().form_valid(form)

