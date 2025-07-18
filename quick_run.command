#!/bin/bash

# Google Indexing API Bulk Tool - Quick Run Script for macOS
# Быстрый запуск без вопросов - использует настройки по умолчанию

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Получаем путь к директории скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 Google Indexing API - Быстрый запуск${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Создаем виртуальное окружение...${NC}"
    python3 -m venv venv
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt > /dev/null 2>&1

# Проверяем наличие файла с URL-ами
if [ ! -f "urls.txt" ]; then
    echo -e "${RED}❌ Файл urls.txt не найден!${NC}"
    echo -e "${YELLOW}📝 Создайте файл urls.txt с URL-ами${NC}"
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

# Проверяем наличие сервисного аккаунта
if [ ! -f "service_account.json" ]; then
    echo -e "${RED}❌ Файл service_account.json не найден!${NC}"
    echo -e "${YELLOW}📝 Скачайте файл сервисного аккаунта из Google Cloud Console${NC}"
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

# Показываем информацию о URL-ах
url_count=$(wc -l < urls.txt)
echo -e "${GREEN}📁 Найдено URL-ов: $url_count${NC}"

# Запускаем отправку с настройками по умолчанию
echo -e "${GREEN}🚀 Запускаем отправку...${NC}"
echo ""

python3 main.py urls.txt --batch-size 100 --max-retries 3 --save-results

# Проверяем результат
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Отправка завершена успешно!${NC}"
else
    echo ""
    echo -e "${RED}❌ Произошла ошибка при отправке${NC}"
fi

echo ""
read -p "Нажмите Enter для выхода..." 