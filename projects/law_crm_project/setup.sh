#!/bin/bash
# Setup script for Law CRM
# Автоматизация настройки и запуска системы

set -e  # Exit on error

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Law CRM - Setup & Installation              ║${NC}"
echo -e "${BLUE}║     CRM для Адвокатського Об'єднання                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Функция для вывода статуса
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Проверка зависимостей
check_dependencies() {
    print_info "Перевірка залежностей..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 не встановлено. Встановіть Python 3.10+"
        exit 1
    fi
    print_status "Python 3 встановлено"
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker не встановлено. Для Docker деплою встановіть Docker"
    else
        print_status "Docker встановлено"
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_warning "Docker Compose не встановлено"
    else
        print_status "Docker Compose встановлено"
    fi
}

# Меню выбора
show_menu() {
    echo ""
    echo -e "${BLUE}Виберіть режим установки:${NC}"
    echo "1) Docker (рекомендовано)"
    echo "2) Локальна установка"
    echo "3) Демонстраційний режим з тестовими даними"
    echo "4) Вихід"
    echo ""
    read -p "Ваш вибір: " choice
    
    case $choice in
        1)
            setup_docker
            ;;
        2)
            setup_local
            ;;
        3)
            setup_demo
            ;;
        4)
            echo "До побачення!"
            exit 0
            ;;
        *)
            print_error "Невірний вибір"
            show_menu
            ;;
    esac
}

# Docker установка
setup_docker() {
    print_info "Установка через Docker..."
    
    # Проверка Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker не встановлено. Встановіть Docker спочатку."
        exit 1
    fi
    
    # Создание .env файла
    if [ ! -f .env ]; then
        print_info "Створення .env файлу..."
        cp .env.example .env
        
        # Генерация SECRET_KEY
        SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
        
        # Обновление .env
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
        else
            # Linux
            sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
        fi
        
        print_status ".env файл створено"
    fi
    
    # Запуск Docker Compose
    print_info "Запуск Docker Compose..."
    docker-compose up -d --build
    
    print_status "Docker контейнери запущено"
    
    # Ожидание запуска БД
    print_info "Очікування запуску БД..."
    sleep 10
    
    # Миграции
    print_info "Виконання міграцій..."
    docker-compose exec -T web python manage.py migrate
    
    print_status "Міграції виконано"
    
    # Создание суперпользователя
    print_info "Створення суперкористувача..."
    echo "Введіть дані адміністратора:"
    docker-compose exec web python manage.py createsuperuser
    
    print_status "Суперкористувач створено"
    
    # Статика
    print_info "Збирання статичних файлів..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    print_status "Статика зібрана"
    
    echo ""
    print_status "${GREEN}Установка завершена!${NC}"
    echo ""
    print_info "Система доступна за адресою:"
    echo -e "  ${BLUE}http://localhost:8000${NC}"
    echo ""
    print_info "Панель адміністрування:"
    echo -e "  ${BLUE}http://localhost:8000/admin${NC}"
    echo ""
    print_info "Для зупинки системи виконайте:"
    echo -e "  ${YELLOW}docker-compose down${NC}"
    echo ""
}

# Локальная установка
setup_local() {
    print_info "Локальна установка..."
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 не встановлено"
        exit 1
    fi
    
    # Создание виртуального окружения
    if [ ! -d "venv" ]; then
        print_info "Створення віртуального оточення..."
        python3 -m venv venv
        print_status "Віртуальне оточення створено"
    fi
    
    # Активация виртуального окружения
    print_info "Активація віртуального оточення..."
    source venv/bin/activate || . venv/Scripts/activate
    
    # Установка зависимостей
    print_info "Установка залежностей..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_status "Залежності встановлено"
    
    # Создание .env
    if [ ! -f .env ]; then
        print_info "Створення .env файлу..."
        cp .env.example .env
        
        # Генерация SECRET_KEY
        SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
            sed -i '' "s/DB_HOST=localhost/DB_HOST=localhost/" .env
        else
            sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
            sed -i "s/DB_HOST=localhost/DB_HOST=localhost/" .env
        fi
        
        print_status ".env файл створено"
    fi
    
    # Проверка PostgreSQL
    print_warning "Переконайтеся, що PostgreSQL встановлено та запущено"
    print_info "Створіть базу даних:"
    echo "  CREATE DATABASE law_crm_db;"
    echo "  CREATE USER law_crm_user WITH PASSWORD 'password';"
    echo "  GRANT ALL PRIVILEGES ON DATABASE law_crm_db TO law_crm_user;"
    echo ""
    read -p "База даних створена? (y/n): " db_ready
    
    if [ "$db_ready" != "y" ]; then
        print_error "Створіть базу даних та повторіть спробу"
        exit 1
    fi
    
    # Миграции
    print_info "Виконання міграцій..."
    python manage.py migrate
    print_status "Міграції виконано"
    
    # Создание суперпользователя
    print_info "Створення суперкористувача..."
    python manage.py createsuperuser
    print_status "Суперкористувач створено"
    
    # Статика
    print_info "Збирання статичних файлів..."
    python manage.py collectstatic --noinput
    print_status "Статика зібрана"
    
    echo ""
    print_status "${GREEN}Локальна установка завершена!${NC}"
    echo ""
    print_info "Для запуску сервера виконайте:"
    echo -e "  ${YELLOW}source venv/bin/activate${NC}"
    echo -e "  ${YELLOW}python manage.py runserver${NC}"
    echo ""
    print_info "Для запуску Celery (в окремих терміналах):"
    echo -e "  ${YELLOW}celery -A law_crm worker -l info${NC}"
    echo -e "  ${YELLOW}celery -A law_crm beat -l info${NC}"
    echo ""
}

# Демонстрационный режим
setup_demo() {
    print_info "Демонстраційний режим з тестовими даними..."
    
    # Запуск Docker установки
    setup_docker
    
    # Загрузка демо данных
    print_info "Завантаження тестових даних..."
    docker-compose exec -T web python manage.py loaddata demo_data.json 2>/dev/null || print_warning "Демо дані не знайдено"
    
    print_status "Демонстраційний режим готовий!"
    echo ""
    print_info "Тестові користувачі:"
    echo -e "  Адмін: ${BLUE}admin / admin123${NC}"
    echo -e "  Адвокат: ${BLUE}lawyer / lawyer123${NC}"
    echo ""
}

# Главная функция
main() {
    check_dependencies
    show_menu
}

# Запуск
main

