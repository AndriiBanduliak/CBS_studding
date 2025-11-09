"""
Celery задачи для интеграции с судебными системами.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import requests
from bs4 import BeautifulSoup
from .models import EGRSRSync, CourtDecision
from case_management.models import Case


@shared_task
def sync_egrsr_cases():
    """
    Периодическая синхронизация дел с ЕГРСР.
    Запускается через Celery Beat каждый день в 22:00.
    """
    # Получаем активные дела с указанным EGRSR ID
    cases = Case.objects.filter(
        status__in=['in_progress', 'suspended'],
        egrsr_id__isnull=False
    ).exclude(egrsr_id='')
    
    synced_count = 0
    errors_count = 0
    
    for case in cases:
        try:
            result = sync_case_with_egrsr(case.id)
            if result['status'] == 'success':
                synced_count += 1
            else:
                errors_count += 1
        except Exception as e:
            errors_count += 1
            print(f"Error syncing case {case.case_number}: {str(e)}")
    
    return f"Synced {synced_count} cases, {errors_count} errors"


@shared_task
def sync_case_with_egrsr(case_id):
    """
    Синхронизация конкретного дела с ЕГРСР.
    
    ВНИМАНИЕ: Это упрощенная реализация. В реальном проекте необходимо:
    1. Использовать официальный API ЕГРСР (если доступен)
    2. Реализовать надежную обработку ошибок
    3. Соблюдать ограничения rate limiting
    4. Использовать аутентификацию, если требуется
    """
    try:
        case = Case.objects.get(id=case_id)
        
        if not case.egrsr_id:
            return {'status': 'failed', 'error': 'No EGRSR ID'}
        
        # Создаем запись синхронизации
        sync = EGRSRSync.objects.create(
            case=case,
            status='failed'  # По умолчанию, изменим если успешно
        )
        
        # Проверяем, есть ли API ключ
        api_key = settings.EGRSR_API_KEY
        api_url = settings.EGRSR_API_URL
        
        if api_key:
            # Вариант 1: Использование API (если доступен)
            response = requests.get(
                f"{api_url}/cases/{case.egrsr_id}",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                sync.response_data = data
                
                # Обработка полученных данных
                decisions = data.get('decisions', [])
                sync.records_found = len(decisions)
                
                new_decisions = 0
                for decision_data in decisions:
                    decision_id = decision_data.get('id')
                    
                    # Проверяем, не существует ли уже такое решение
                    if not CourtDecision.objects.filter(decision_id=decision_id).exists():
                        CourtDecision.objects.create(
                            case=case,
                            decision_id=decision_id,
                            decision_date=decision_data.get('date'),
                            decision_type=decision_data.get('type', 'Рішення'),
                            judge_name=decision_data.get('judge', ''),
                            summary=decision_data.get('summary', ''),
                            full_text=decision_data.get('full_text', ''),
                            pdf_url=decision_data.get('pdf_url', ''),
                            egrsr_url=decision_data.get('url', ''),
                        )
                        new_decisions += 1
                
                sync.new_decisions = new_decisions
                sync.status = 'success'
                sync.save()
                
                # Обновляем дату последней синхронизации
                case.last_egrsr_sync = timezone.now()
                case.save()
                
                return {
                    'status': 'success',
                    'records_found': sync.records_found,
                    'new_decisions': new_decisions
                }
        
        else:
            # Вариант 2: Парсинг веб-страницы (если API недоступен)
            # ВНИМАНИЕ: Парсинг может нарушать ToS, использовать с осторожностью
            url = f"https://reyestr.court.gov.ua/Review/{case.egrsr_id}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Простой пример парсинга (нужно адаптировать под реальную структуру сайта)
                # Это демонстрационный код
                decisions = soup.find_all('div', class_='decision-item')
                sync.records_found = len(decisions)
                
                # В реальном проекте здесь была бы детальная обработка
                sync.status = 'partial'
                sync.error_message = 'Парсинг потребує адаптації під структуру сайту'
                sync.save()
                
                return {
                    'status': 'partial',
                    'message': 'Parsing requires adaptation'
                }
        
        sync.error_message = 'No API key configured and parsing not implemented'
        sync.save()
        
        return {
            'status': 'failed',
            'error': 'No API key configured'
        }
    
    except requests.RequestException as e:
        sync.status = 'failed'
        sync.error_message = f'Network error: {str(e)}'
        sync.save()
        
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    except Case.DoesNotExist:
        return {
            'status': 'failed',
            'error': f'Case {case_id} not found'
        }
    
    except Exception as e:
        if 'sync' in locals():
            sync.status = 'failed'
            sync.error_message = str(e)
            sync.save()
        
        return {
            'status': 'failed',
            'error': str(e)
        }

