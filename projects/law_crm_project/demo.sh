#!/bin/bash
# Demo script for Law CRM
# Демонстрация функционала системы

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Функции вывода
print_header() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  $1${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}➜${NC} $1"
    sleep 1
}

print_demo() {
    echo -e "${MAGENTA}[DEMO]${NC} $1"
    sleep 2
}

print_code() {
    echo -e "${YELLOW}$1${NC}"
}

# Проверка запущенной системы
check_system() {
    if ! docker-compose ps | grep -q "web.*Up"; then
        echo -e "${RED}Система не запущена!${NC}"
        echo "Запустіть систему командою: ./setup.sh"
        exit 1
    fi
}

# Демонстрация
print_header "LAW CRM - ДЕМОНСТРАЦІЯ СИСТЕМИ"

echo -e "${BLUE}Ця демонстрація покаже основні можливості системи:${NC}"
echo "1. Управління клієнтами"
echo "2. Управління справами"
echo "3. Облік часу"
echo "4. Генерація документів"
echo "5. Біллінг"
echo "6. Інтеграція з ЄДРСР"
echo ""
read -p "Натисніть Enter для початку демонстрації..."

# Проверка системы
check_system

print_header "1. УПРАВЛІННЯ КЛІЄНТАМИ"

print_demo "Система підтримує роботу з фізичними та юридичними особами"

print_step "Створення клієнта (фізична особа) через Django shell:"
print_code "docker-compose exec web python manage.py shell"

cat << 'EOF'

from core.models import Client, User

# Создание клиента - физическое лицо
client = Client.objects.create(
    client_type='individual',
    first_name='Іван',
    last_name='Петренко',
    middle_name='Миколайович',
    rnokpp='1234567890',
    email='ivan.petrenko@example.com',
    phone='+380501234567',
    address='м. Київ, вул. Хрещатик, 1',
    is_active=True
)
print(f"Клієнт створено: {client}")

EOF

print_step "✓ Система зберігає РНОКПП та паспортні дані"
print_step "✓ Автоматична перевірка конфлікту інтересів"

print_header "2. УПРАВЛІННЯ СПРАВАМИ"

print_demo "Система використовує FSM (Finite State Machine) для управління стадіями справи"

print_step "Створення справи:"
print_code "python manage.py shell"

cat << 'EOF'

from case_management.models import Case, Court
from core.models import Client, User

# Получаем клиента и адвоката
client = Client.objects.first()
lawyer = User.objects.filter(role='lawyer').first()

# Создаем справу
case = Case.objects.create(
    case_number='910/1234/23',
    title='Позов про стягнення боргу',
    description='Стягнення заборгованості за договором',
    proceeding_type='civil',
    client=client,
    opposing_party='ТОВ "Боржник"',
    responsible_lawyer=lawyer,
    status='new'
)
print(f"Справа створена: {case}")

# FSM переходы
case.start_consultation()
case.save()
print(f"Статус: {case.get_status_display()}")

case.prepare_contract()
case.save()
print(f"Статус: {case.get_status_display()}")

case.start_work()
case.save()
print(f"Статус: {case.get_status_display()}")

EOF

print_step "✓ Процесуальна воронка: Нова → Консультація → Підготовка → В роботі → Закрита"
print_step "✓ Контроль процесуальних строків"
print_step "✓ Облік ордерів адвокатів"

print_header "3. ОБЛІК ЧАСУ (TIME TRACKING)"

print_demo "Адвокати можуть відслідковувати час роботи по справах"

print_step "Запуск таймера:"
print_code "Відкрийте: http://localhost:8000/time/timer/"

print_step "Або створення запису вручну:"

cat << 'EOF'

from time_tracking.models import TimeEntry, WorkType
from case_management.models import Case
from core.models import User

# Создаем тип работы
work_type, _ = WorkType.objects.get_or_create(
    name='Консультація',
    defaults={'default_rate': 1500, 'is_billable': True}
)

# Создаем запись времени
time_entry = TimeEntry.objects.create(
    user=User.objects.filter(role='lawyer').first(),
    case=Case.objects.first(),
    work_type=work_type,
    date='2024-01-15',
    duration_hours=2.5,
    description='Консультація клієнта, аналіз документів',
    hourly_rate=1500,
    is_billable=True
)
print(f"Запис створено: {time_entry}")
print(f"Вартість: {time_entry.total_amount} грн")

EOF

print_step "✓ Таймер в реальному часі"
print_step "✓ Автоматичний розрахунок вартості"
print_step "✓ Звіти по адвокатам та справам"

print_header "4. ГЕНЕРАЦІЯ ДОКУМЕНТІВ"

print_demo "Автоматична генерація документів з шаблонів"

print_step "Шаблони підтримують змінні:"
print_code "{{case_number}}, {{client_name}}, {{court_name}}, {{date}}"

print_step "Приклад генерації договору:"

cat << 'EOF'

from documents.models import DocumentTemplate
from case_management.models import Case

# Создаем шаблон договора
template = DocumentTemplate.objects.create(
    name='Договір про надання правової допомоги',
    document_type='contract',
    is_active=True
)

# Генерируем документ для дела
case = Case.objects.first()
context_data = {
    'case_number': case.case_number,
    'client_name': case.client.full_name,
    'date': '15.01.2024',
    'lawyer_name': 'Адвокат Іванов І.І.',
}

# generated_doc = template.generate_document(context_data)

EOF

print_step "✓ Шаблони у форматі .docx"
print_step "✓ Автоматична підстановка даних"
print_step "✓ Повнотекстовий пошук документів (PostgreSQL)"

print_header "5. БІЛЛІНГ"

print_demo "Автоматична генерація рахунків на основі обліку часу"

print_step "Створення рахунку:"

cat << 'EOF'

from billing.models import Invoice
from case_management.models import Case
from datetime import date, timedelta

case = Case.objects.first()

# Создаем счет
invoice = Invoice.objects.create(
    invoice_number='2024-001',
    case=case,
    client=case.client,
    issue_date=date.today(),
    due_date=date.today() + timedelta(days=14),
    lawyer_name='Адвокат Іванов І.І.',
    lawyer_certificate='№12345',
    status='draft'
)

# Автоматический расчет на основе времени
invoice.calculate_from_time_entries()

print(f"Рахунок створено: {invoice}")
print(f"Сума без ПДВ: {invoice.subtotal} грн")
print(f"ПДВ (20%): {invoice.tax_amount} грн")
print(f"Всього: {invoice.total} грн")

EOF

print_step "✓ Автоматичний розрахунок з обліку часу"
print_step "✓ ПДВ 20%"
print_step "✓ Експорт у PDF"
print_step "✓ Облік платежів"

print_header "6. ІНТЕГРАЦІЯ З ЄДРСР"

print_demo "Автоматична синхронізація з Єдиним державним реєстром судових рішень"

print_step "Celery задачі:"
print_code "# Перевірка строків (щодня о 9:00)"
print_code "celery -A law_crm beat"

print_step "Ручна синхронізація:"

cat << 'EOF'

from court_integrations.tasks import sync_case_with_egrsr
from case_management.models import Case

# Устанавливаем EGRSR ID для дела
case = Case.objects.first()
case.egrsr_id = 'some-egrsr-id'
case.save()

# Запускаем синхронизацию
result = sync_case_with_egrsr(case.id)
print(result)

EOF

print_step "✓ Автоматичне завантаження судових рішень"
print_step "✓ Сповіщення про нові рішення"
print_step "✓ Щоденна синхронізація о 22:00"

print_header "7. БЕЗПЕКА ТА АУДИТ"

print_demo "Система забезпечує повний аудит дій"

print_step "Перегляд історії змін:"

cat << 'EOF'

from auditlog.models import LogEntry
from case_management.models import Case

case = Case.objects.first()

# Получаем историю изменений
history = LogEntry.objects.get_for_object(case)

for entry in history:
    print(f"{entry.timestamp}: {entry.action} by {entry.actor}")
    print(f"Зміни: {entry.changes}")

EOF

print_step "✓ Аудит всіх змін (django-auditlog)"
print_step "✓ RBAC: Адвокат, Помічник, Партнер, Адміністратор"
print_step "✓ Object-level permissions"
print_step "✓ Шифрування конфіденційних даних"

print_header "ДОСТУП ДО СИСТЕМИ"

echo -e "${GREEN}Система запущена та доступна за адресою:${NC}"
echo ""
echo -e "  🌐 Web-інтерфейс: ${BLUE}http://localhost:8000${NC}"
echo -e "  🔐 Адмін-панель:  ${BLUE}http://localhost:8000/admin${NC}"
echo ""
echo -e "${YELLOW}Для входу використовуйте створеного суперкористувача${NC}"
echo ""

print_header "КОРИСНІ КОМАНДИ"

echo -e "${GREEN}Docker команди:${NC}"
echo "  docker-compose up -d          # Запустити систему"
echo "  docker-compose down           # Зупинити систему"
echo "  docker-compose logs -f web    # Переглянути логи"
echo "  docker-compose exec web bash  # Відкрити shell в контейнері"
echo ""

echo -e "${GREEN}Django команди:${NC}"
echo "  python manage.py shell        # Django shell"
echo "  python manage.py migrate      # Міграції"
echo "  python manage.py createsuperuser  # Створити адміна"
echo ""

echo -e "${GREEN}Celery команди:${NC}"
echo "  celery -A law_crm worker -l info  # Запустити worker"
echo "  celery -A law_crm beat -l info    # Запустити beat (періодичні задачі)"
echo ""

print_header "ЗАВЕРШЕННЯ ДЕМОНСТРАЦІЇ"

echo -e "${GREEN}Дякуємо за увагу!${NC}"
echo ""
echo -e "Повна документація: ${BLUE}README.md${NC}"
echo -e "Підтримка: contact@lawcrm.example.com"
echo ""

