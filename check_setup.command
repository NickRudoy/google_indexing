#!/bin/bash

# Google Indexing API - Диагностика и проверка настройки
# Проверяет все компоненты системы

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Получаем путь к директории скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🔍 Google Indexing API - Диагностика${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Проверяем Python
echo -e "${YELLOW}🐍 Проверяем Python...${NC}"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo -e "${GREEN}✅ $python_version${NC}"
else
    echo -e "${RED}❌ Python3 не найден${NC}"
    exit 1
fi

# Проверяем виртуальное окружение
echo -e "${YELLOW}📦 Проверяем виртуальное окружение...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Виртуальное окружение найдено${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Виртуальное окружение не найдено${NC}"
    echo -e "${BLUE}   Создаем новое...${NC}"
    python3 -m venv venv
    source venv/bin/activate
fi

# Проверяем зависимости
echo -e "${YELLOW}📦 Проверяем зависимости...${NC}"
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt найден${NC}"
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✅ Зависимости установлены${NC}"
else
    echo -e "${RED}❌ requirements.txt не найден${NC}"
    exit 1
fi

# Проверяем сервисный аккаунт
echo -e "${YELLOW}🔑 Проверяем сервисный аккаунт...${NC}"
if [ -f "service_account.json" ]; then
    echo -e "${GREEN}✅ service_account.json найден${NC}"
    python setup_service_account.py
else
    echo -e "${RED}❌ service_account.json не найден${NC}"
    echo -e "${YELLOW}📝 Скачайте файл из Google Cloud Console${NC}"
fi

# Проверяем URL-ы
echo -e "${YELLOW}📁 Проверяем URL-ы...${NC}"
if [ -f "urls.txt" ]; then
    url_count=$(wc -l < urls.txt)
    echo -e "${GREEN}✅ urls.txt найден ($url_count URL-ов)${NC}"
    
    # Показываем первые URL-ы
    echo -e "${BLUE}   Первые URL-ы:${NC}"
    head -3 urls.txt | while read url; do
        echo -e "   • $url"
    done
    
    if [ $url_count -gt 3 ]; then
        echo -e "   ... и еще $((url_count - 3)) URL-ов"
    fi
else
    echo -e "${YELLOW}⚠️  urls.txt не найден${NC}"
    echo -e "${BLUE}   Создайте файл с URL-ами для тестирования${NC}"
fi

echo ""
echo -e "${BLUE}🧪 Тестируем подключение к API...${NC}"

# Тестируем API
if [ -f "urls.txt" ]; then
    first_url=$(head -1 urls.txt)
    if [ ! -z "$first_url" ]; then
        echo -e "${BLUE}   Тестируем URL: $first_url${NC}"
        python check_permissions.py --test-url "$first_url"
    fi
else
    echo -e "${YELLOW}   Нет URL-ов для тестирования${NC}"
fi

echo ""
echo -e "${BLUE}📊 Статус системы:${NC}"

# Проверяем все файлы
files_status=0
echo -e "${YELLOW}📄 Проверяем файлы:${NC}"

if [ -f "main.py" ]; then
    echo -e "${GREEN}   ✅ main.py${NC}"
else
    echo -e "${RED}   ❌ main.py${NC}"
    files_status=1
fi

if [ -f "check_permissions.py" ]; then
    echo -e "${GREEN}   ✅ check_permissions.py${NC}"
else
    echo -e "${RED}   ❌ check_permissions.py${NC}"
    files_status=1
fi

if [ -f "setup_service_account.py" ]; then
    echo -e "${GREEN}   ✅ setup_service_account.py${NC}"
else
    echo -e "${RED}   ❌ setup_service_account.py${NC}"
    files_status=1
fi

if [ -f "run_indexing.command" ]; then
    echo -e "${GREEN}   ✅ run_indexing.command${NC}"
else
    echo -e "${RED}   ❌ run_indexing.command${NC}"
    files_status=1
fi

if [ -f "quick_run.command" ]; then
    echo -e "${GREEN}   ✅ quick_run.command${NC}"
else
    echo -e "${RED}   ❌ quick_run.command${NC}"
    files_status=1
fi

echo ""
if [ $files_status -eq 0 ]; then
    echo -e "${GREEN}✅ Система готова к работе!${NC}"
    echo -e "${BLUE}🚀 Для запуска используйте:${NC}"
    echo -e "${BLUE}   • Двойной клик на quick_run.command (быстрый запуск)${NC}"
    echo -e "${BLUE}   • Двойной клик на run_indexing.command (с настройками)${NC}"
else
    echo -e "${RED}❌ Обнаружены проблемы с файлами${NC}"
fi

echo ""
echo -e "${BLUE}📖 Документация:${NC}"
echo -e "${BLUE}   • README.MD - основная документация${NC}"
echo -e "${BLUE}   • SETUP_GUIDE.md - руководство по настройке${NC}"

echo ""
read -p "Нажмите Enter для выхода..." 