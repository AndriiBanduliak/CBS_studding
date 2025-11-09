#!/usr/bin/env python
"""
Скрипт для создания демонстрационных данных.
Запуск: python manage.py shell < scripts/create_demo_data.py
"""

from django.contrib.auth import get_user_model
from core.models import Client, ConflictCheck
from case_management.models import Case, Court, LawyerOrder, CaseEvent
from time_tracking.models import WorkType, TimeEntry
from documents.models import DocumentCategory
from datetime import date, datetime, timedelta

User = get_user_model()

print("=" * 60)
print("Створення демонстраційних даних для Law CRM")
print("=" * 60)

# 1. Создание пользователей
print("\n1. Створення користувачів...")

# Партнер
partner, created = User.objects.get_or_create(
    username='partner',
    defaults={
        'first_name': 'Олександр',
        'last_name': 'Іванов',
        'email': 'partner@lawfirm.ua',
        'role': 'partner',
        'naau_certificate_number': '№12345',
        'hourly_rate': 2000,
        'is_staff': True,
        'is_active': True,
    }
)
if created:
    partner.set_password('partner123')
    partner.save()
    print(f"  ✓ Партнер: {partner.username}")

# Адвокат 1
lawyer1, created = User.objects.get_or_create(
    username='lawyer1',
    defaults={
        'first_name': 'Марія',
        'last_name': 'Петренко',
        'email': 'lawyer1@lawfirm.ua',
        'role': 'lawyer',
        'naau_certificate_number': '№23456',
        'hourly_rate': 1500,
        'is_active': True,
    }
)
if created:
    lawyer1.set_password('lawyer123')
    lawyer1.save()
    print(f"  ✓ Адвокат: {lawyer1.username}")

# Адвокат 2
lawyer2, created = User.objects.get_or_create(
    username='lawyer2',
    defaults={
        'first_name': 'Дмитро',
        'last_name': 'Сидоренко',
        'email': 'lawyer2@lawfirm.ua',
        'role': 'lawyer',
        'naau_certificate_number': '№34567',
        'hourly_rate': 1500,
        'is_active': True,
    }
)
if created:
    lawyer2.set_password('lawyer123')
    lawyer2.save()
    print(f"  ✓ Адвокат: {lawyer2.username}")

# Помощник
assistant, created = User.objects.get_or_create(
    username='assistant',
    defaults={
        'first_name': 'Олена',
        'last_name': 'Коваленко',
        'email': 'assistant@lawfirm.ua',
        'role': 'assistant',
        'is_active': True,
    }
)
if created:
    assistant.set_password('assistant123')
    assistant.save()
    print(f"  ✓ Помічник: {assistant.username}")

# 2. Создание клиентов
print("\n2. Створення клієнтів...")

# Клиент - физическое лицо
client1, created = Client.objects.get_or_create(
    rnokpp='1234567890',
    defaults={
        'client_type': 'individual',
        'first_name': 'Іван',
        'last_name': 'Шевченко',
        'middle_name': 'Петрович',
        'email': 'ivan.shevchenko@example.com',
        'phone': '+380501234567',
        'address': 'м. Київ, вул. Хрещатик, 1, кв. 10',
        'responsible_lawyer': lawyer1,
        'is_active': True,
    }
)
if created:
    print(f"  ✓ Клієнт (ФО): {client1.full_name}")

# Клиент - юридическое лицо
client2, created = Client.objects.get_or_create(
    edrpou='12345678',
    defaults={
        'client_type': 'legal',
        'company_name': 'ТОВ "Будівельна Компанія"',
        'email': 'info@budcompany.ua',
        'phone': '+380445551234',
        'address': 'м. Київ, вул. Промислова, 25',
        'representative_name': 'Петров Петро Петрович',
        'representative_position': 'Директор',
        'responsible_lawyer': lawyer2,
        'is_active': True,
    }
)
if created:
    print(f"  ✓ Клієнт (ЮО): {client2.company_name}")

# Клиент 3
client3, created = Client.objects.get_or_create(
    rnokpp='9876543210',
    defaults={
        'client_type': 'individual',
        'first_name': 'Наталія',
        'last_name': 'Бондаренко',
        'middle_name': 'Олександрівна',
        'email': 'natalia.bondarenko@example.com',
        'phone': '+380679876543',
        'address': 'м. Харків, проспект Науки, 5',
        'responsible_lawyer': lawyer1,
        'is_active': True,
    }
)
if created:
    print(f"  ✓ Клієнт (ФО): {client3.full_name}")

# 3. Создание судов
print("\n3. Створення судів...")

court1, created = Court.objects.get_or_create(
    name='Печерський районний суд м. Києва',
    defaults={
        'court_type': 'local',
        'address': 'м. Київ, вул. Хрещатик, 42',
        'phone': '+380445551111',
        'email': 'office@pechersk.court.gov.ua',
    }
)
if created:
    print(f"  ✓ Суд: {court1.name}")

court2, created = Court.objects.get_or_create(
    name='Київський апеляційний суд',
    defaults={
        'court_type': 'appeal',
        'address': 'м. Київ, вул. Солом\'янська, 2а',
        'phone': '+380445552222',
    }
)
if created:
    print(f"  ✓ Суд: {court2.name}")

# 4. Создание дел
print("\n4. Створення справ...")

case1, created = Case.objects.get_or_create(
    case_number='910/1234/24',
    defaults={
        'title': 'Позов про стягнення заборгованості',
        'description': 'Стягнення заборгованості за договором поставки товарів на суму 150 000 грн',
        'proceeding_type': 'civil',
        'client': client1,
        'opposing_party': 'ТОВ "Боржник і Ко"',
        'opposing_party_lawyer': 'Адвокат Сидоров С.С.',
        'court': court1,
        'judge': 'Коваль О.О.',
        'responsible_lawyer': lawyer1,
        'status': 'in_progress',
        'registration_date': date.today() - timedelta(days=30),
        'next_hearing_date': datetime.now() + timedelta(days=14, hours=10),
        'estimated_value': 150000,
        'contract_amount': 25000,
        'is_priority': True,
    }
)
if created:
    case1.lawyers.add(lawyer1)
    case1.assistants.add(assistant)
    print(f"  ✓ Справа: {case1.case_number}")

case2, created = Case.objects.get_or_create(
    case_number='910/5678/24',
    defaults={
        'title': 'Справа про розірвання договору оренди',
        'description': 'Позов про дострокове розірвання договору оренди нежитлового приміщення',
        'proceeding_type': 'economic',
        'client': client2,
        'opposing_party': 'ПП "Орендодавець"',
        'court': court1,
        'judge': 'Мельник В.В.',
        'responsible_lawyer': lawyer2,
        'status': 'in_progress',
        'registration_date': date.today() - timedelta(days=45),
        'next_hearing_date': datetime.now() + timedelta(days=7, hours=14),
        'estimated_value': 200000,
        'contract_amount': 30000,
        'is_priority': False,
    }
)
if created:
    case2.lawyers.add(lawyer2)
    print(f"  ✓ Справа: {case2.case_number}")

case3, created = Case.objects.get_or_create(
    case_number='910/9999/24',
    defaults={
        'title': 'Адміністративна справа про оскарження рішення',
        'description': 'Оскарження рішення місцевої адміністрації',
        'proceeding_type': 'administrative',
        'client': client3,
        'opposing_party': 'Київська міська адміністрація',
        'court': court2,
        'responsible_lawyer': lawyer1,
        'status': 'consultation',
        'registration_date': date.today() - timedelta(days=5),
        'contract_amount': 15000,
    }
)
if created:
    case3.lawyers.add(lawyer1, partner)
    print(f"  ✓ Справа: {case3.case_number}")

# 5. Типы работ
print("\n5. Створення типів робіт...")

work_types_data = [
    ('Консультація', 1500, True),
    ('Підготовка процесуальних документів', 1800, True),
    ('Участь у судовому засіданні', 2500, True),
    ('Вивчення матеріалів справи', 1200, True),
    ('Переговори з протилежною стороною', 1500, True),
    ('Юридичний аналіз', 1500, True),
]

work_types = []
for name, rate, billable in work_types_data:
    wt, created = WorkType.objects.get_or_create(
        name=name,
        defaults={
            'default_rate': rate,
            'is_billable': billable,
            'is_active': True,
        }
    )
    work_types.append(wt)
    if created:
        print(f"  ✓ Тип роботи: {name}")

# 6. Записи учета времени
print("\n6. Створення записів обліку часу...")

time_entries_data = [
    (lawyer1, case1, work_types[0], date.today() - timedelta(days=5), 2.0, 'Первинна консультація клієнта'),
    (lawyer1, case1, work_types[1], date.today() - timedelta(days=4), 3.5, 'Підготовка позовної заяви'),
    (lawyer1, case1, work_types[3], date.today() - timedelta(days=3), 2.0, 'Аналіз документів клієнта'),
    (lawyer2, case2, work_types[0], date.today() - timedelta(days=6), 1.5, 'Консультація представника компанії'),
    (lawyer2, case2, work_types[1], date.today() - timedelta(days=5), 4.0, 'Підготовка клопотання'),
    (lawyer1, case3, work_types[0], date.today() - timedelta(days=2), 1.0, 'Первинна консультація'),
]

for user, case, work_type, entry_date, hours, desc in time_entries_data:
    te, created = TimeEntry.objects.get_or_create(
        user=user,
        case=case,
        work_type=work_type,
        date=entry_date,
        defaults={
            'duration_hours': hours,
            'description': desc,
            'hourly_rate': user.hourly_rate,
            'is_billable': True,
        }
    )
    if created:
        print(f"  ✓ Запис: {user.last_name} - {case.case_number} ({hours}h)")

# 7. События
print("\n7. Створення подій...")

events_data = [
    (case1, 'hearing', 'Підготовче судове засідання', datetime.now() + timedelta(days=14, hours=10)),
    (case1, 'deadline', 'Строк подання додаткових доказів', datetime.now() + timedelta(days=7)),
    (case2, 'hearing', 'Розгляд справи по суті', datetime.now() + timedelta(days=7, hours=14)),
    (case2, 'meeting', 'Зустріч з клієнтом', datetime.now() + timedelta(days=2, hours=15)),
]

for case, event_type, title, event_date in events_data:
    ce, created = CaseEvent.objects.get_or_create(
        case=case,
        title=title,
        defaults={
            'event_type': event_type,
            'event_date': event_date,
            'location': case.court.name if case.court else 'Офіс',
            'is_completed': False,
        }
    )
    if created:
        print(f"  ✓ Подія: {title}")

# 8. Категории документов
print("\n8. Створення категорій документів...")

categories_data = [
    'Договори',
    'Позовні заяви',
    'Клопотання',
    'Апеляційні скарги',
    'Докази',
    'Рішення судів',
    'Листування',
]

for cat_name in categories_data:
    dc, created = DocumentCategory.objects.get_or_create(
        name=cat_name,
        defaults={'description': f'Категорія: {cat_name}'}
    )
    if created:
        print(f"  ✓ Категорія: {cat_name}")

print("\n" + "=" * 60)
print("✓ Демонстраційні дані успішно створено!")
print("=" * 60)
print("\nТестові користувачі:")
print(f"  Партнер:   username=partner,   password=partner123")
print(f"  Адвокат 1: username=lawyer1,   password=lawyer123")
print(f"  Адвокат 2: username=lawyer2,   password=lawyer123")
print(f"  Помічник:  username=assistant, password=assistant123")
print("\nСтворено:")
print(f"  - Користувачів: 4")
print(f"  - Клієнтів: 3")
print(f"  - Судів: 2")
print(f"  - Справ: 3")
print(f"  - Записів обліку часу: 6")
print(f"  - Подій: 4")
print(f"  - Категорій документів: 7")
print("\nСистема готова до демонстрації!")
print("=" * 60)

