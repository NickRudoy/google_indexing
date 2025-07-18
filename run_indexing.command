#!/bin/bash

# Google Indexing API Bulk Tool - Executable Script for macOS
# SEO специалист просто кликает на этот файл и все запускается автоматически

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Получаем путь к директории скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 Google Indexing API Bulk Tool${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Создаем виртуальное окружение...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Ошибка создания виртуального окружения${NC}"
        read -p "Нажмите Enter для выхода..."
        exit 1
    fi
fi

# Активируем виртуальное окружение
echo -e "${YELLOW}🔧 Активируем виртуальное окружение...${NC}"
source venv/bin/activate

# Устанавливаем зависимости
echo -e "${YELLOW}📦 Проверяем зависимости...${NC}"
pip install -r requirements.txt > /dev/null 2>&1

# Проверяем наличие файла с URL-ами
if [ ! -f "urls.txt" ]; then
    echo -e "${RED}❌ Файл urls.txt не найден!${NC}"
    echo -e "${YELLOW}📝 Создайте файл urls.txt с URL-ами (по одному на строку)${NC}"
    echo ""
    echo -e "${BLUE}Пример содержимого urls.txt:${NC}"
    echo "https://example.com/page1"
    echo "https://example.com/page2"
    echo "https://example.com/page3"
    echo ""
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

# Проверяем наличие сервисного аккаунта
if [ ! -f "service_account.json" ]; then
    echo -e "${RED}❌ Файл service_account.json не найден!${NC}"
    echo -e "${YELLOW}📝 Скачайте файл сервисного аккаунта из Google Cloud Console${NC}"
    echo -e "${YELLOW}📝 Переименуйте в service_account.json и поместите в эту папку${NC}"
    echo ""
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

# Проверяем настройку сервисного аккаунта
echo -e "${YELLOW}🔍 Проверяем настройку сервисного аккаунта...${NC}"
python3 setup_service_account.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Проблемы с настройкой сервисного аккаунта${NC}"
    echo -e "${YELLOW}📝 Запустите: python3 setup_service_account.py --setup-instructions${NC}"
    echo ""
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

# Показываем информацию о URL-ах
echo -e "${GREEN}📁 Найдены URL-ы в urls.txt:${NC}"
url_count=$(wc -l < urls.txt)
echo -e "${BLUE}   Количество URL-ов: $url_count${NC}"

# Показываем первые несколько URL-ов
echo -e "${BLUE}   Первые URL-ы:${NC}"
head -3 urls.txt | while read url; do
    echo -e "   • $url"
done

if [ $url_count -gt 3 ]; then
    echo -e "   ... и еще $((url_count - 3)) URL-ов"
fi

echo ""

# Спрашиваем пользователя о настройках
echo -e "${YELLOW}⚙️  Настройки отправки:${NC}"
echo -e "${BLUE}   1. Размер пакета (по умолчанию: 100):${NC}"
read -p "   Введите размер пакета (Enter для пропуска): " batch_size
batch_size=${batch_size:-100}

echo -e "${BLUE}   2. Количество повторных попыток (по умолчанию: 3):${NC}"
read -p "   Введите количество попыток (Enter для пропуска): " max_retries
max_retries=${max_retries:-3}

echo -e "${BLUE}   3. Сохранить результаты в файл? (y/n, по умолчанию: y):${NC}"
read -p "   Сохранить результаты? (Enter для пропуска): " save_results
save_results=${save_results:-y}

echo ""

# Подтверждение запуска
echo -e "${YELLOW}🚀 Готов к запуску!${NC}"
echo -e "${BLUE}   URL-ов: $url_count${NC}"
echo -e "${BLUE}   Размер пакета: $batch_size${NC}"
echo -e "${BLUE}   Повторных попыток: $max_retries${NC}"
echo -e "${BLUE}   Сохранение результатов: $save_results${NC}"
echo ""

read -p "Нажмите Enter для запуска или Ctrl+C для отмены..."

# Запускаем отправку
echo -e "${GREEN}🚀 Запускаем отправку URL-ов...${NC}"
echo ""

if [ "$save_results" = "y" ] || [ "$save_results" = "Y" ]; then
    python3 main.py urls.txt --batch-size $batch_size --max-retries $max_retries --save-results
else
    python3 main.py urls.txt --batch-size $batch_size --max-retries $max_retries
fi

# Проверяем результат
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Отправка завершена успешно!${NC}"
    
    # Показываем созданные файлы
    if [ -f "indexing.log" ]; then
        echo -e "${BLUE}📄 Лог файл: indexing.log${NC}"
    fi
    
    if ls indexing_results_*.json 1> /dev/null 2>&1; then
        echo -e "${BLUE}📄 Результаты: indexing_results_*.json${NC}"
    fi
else
    echo ""
    echo -e "${RED}❌ Произошла ошибка при отправке${NC}"
    echo -e "${YELLOW}📝 Проверьте логи в indexing.log${NC}"
fi

echo ""
echo -e "${BLUE}🔍 Для диагностики запустите: python3 check_permissions.py${NC}"
echo -e "${BLUE}📖 Подробная документация: README.MD${NC}"

# Ждем нажатия клавиши перед закрытием
echo ""
read -p "Нажмите Enter для выхода..." 