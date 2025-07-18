#!/bin/bash

# Google Indexing API - Автоматическая установка
# Устанавливает все зависимости и настраивает окружение

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Получаем путь к директории скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${PURPLE}🚀 Google Indexing API - Автоматическая установка${NC}"
echo -e "${PURPLE}==============================================${NC}"
echo ""

# Функция для проверки команды
check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Функция для установки Homebrew
install_homebrew() {
    echo -e "${YELLOW}🍺 Устанавливаем Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Добавляем Homebrew в PATH
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
}

# Шаг 1: Проверяем и устанавливаем Python
echo -e "${BLUE}📋 Шаг 1: Проверка Python${NC}"
echo -e "${CYAN}================================${NC}"

if check_command python3; then
    python_version=$(python3 --version)
    echo -e "${GREEN}✅ $python_version уже установлен${NC}"
else
    echo -e "${YELLOW}⚠️  Python3 не найден${NC}"
    
    # Проверяем Homebrew
    if check_command brew; then
        echo -e "${BLUE}📦 Устанавливаем Python через Homebrew...${NC}"
        brew install python
    else
        echo -e "${YELLOW}📦 Homebrew не найден${NC}"
        read -p "Установить Homebrew для установки Python? (y/n): " install_brew
        if [[ $install_brew == "y" || $install_brew == "Y" ]]; then
            install_homebrew
            echo -e "${BLUE}📦 Устанавливаем Python...${NC}"
            brew install python
        else
            echo -e "${RED}❌ Python необходим для работы приложения${NC}"
            echo -e "${YELLOW}📝 Установите Python вручную с https://python.org${NC}"
            exit 1
        fi
    fi
fi

# Проверяем версию Python
python_version_check=$(python3 -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
required_version="3.7"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    echo -e "${GREEN}✅ Версия Python $python_version_check подходит${NC}"
else
    echo -e "${RED}❌ Требуется Python 3.7 или выше${NC}"
    echo -e "${YELLOW}📝 Текущая версия: $python_version_check${NC}"
    exit 1
fi

echo ""

# Шаг 2: Создаем виртуальное окружение
echo -e "${BLUE}📋 Шаг 2: Настройка виртуального окружения${NC}"
echo -e "${CYAN}==========================================${NC}"

if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Виртуальное окружение уже существует${NC}"
    read -p "Пересоздать виртуальное окружение? (y/n): " recreate_venv
    if [[ $recreate_venv == "y" || $recreate_venv == "Y" ]]; then
        echo -e "${BLUE}🗑️  Удаляем старое виртуальное окружение...${NC}"
        rm -rf venv
        echo -e "${BLUE}📦 Создаем новое виртуальное окружение...${NC}"
        python3 -m venv venv
    fi
else
    echo -e "${BLUE}📦 Создаем виртуальное окружение...${NC}"
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo -e "${BLUE}🔧 Активируем виртуальное окружение...${NC}"
source venv/bin/activate

# Обновляем pip
echo -e "${BLUE}📦 Обновляем pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

echo ""

# Шаг 3: Устанавливаем зависимости
echo -e "${BLUE}📋 Шаг 3: Установка зависимостей${NC}"
echo -e "${CYAN}==============================${NC}"

if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📦 Устанавливаем зависимости из requirements.txt...${NC}"
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Зависимости установлены успешно${NC}"
    else
        echo -e "${RED}❌ Ошибка установки зависимостей${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Файл requirements.txt не найден${NC}"
    echo -e "${BLUE}📦 Устанавливаем основные зависимости...${NC}"
    
    # Устанавливаем основные пакеты
    pip install google-auth google-auth-oauthlib google-auth-httplib2 requests
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Основные зависимости установлены${NC}"
    else
        echo -e "${RED}❌ Ошибка установки зависимостей${NC}"
        exit 1
    fi
fi

echo ""

# Шаг 4: Проверяем и создаем необходимые файлы
echo -e "${BLUE}📋 Шаг 4: Проверка файлов${NC}"
echo -e "${CYAN}========================${NC}"

# Проверяем service_account.json
if [ -f "service_account.json" ]; then
    echo -e "${GREEN}✅ service_account.json найден${NC}"
else
    echo -e "${YELLOW}⚠️  service_account.json не найден${NC}"
    echo -e "${BLUE}📝 Создаем шаблон файла...${NC}"
    
    cat > service_account.json.template << 'EOF'
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
EOF
    
    echo -e "${YELLOW}📝 Создан шаблон service_account.json.template${NC}"
    echo -e "${BLUE}📖 Инструкции по настройке:${NC}"
    echo -e "${BLUE}   1. Скачайте JSON файл из Google Cloud Console${NC}"
    echo -e "${BLUE}   2. Переименуйте в service_account.json${NC}"
    echo -e "${BLUE}   3. Поместите в эту папку${NC}"
fi

# Проверяем urls.txt
if [ -f "urls.txt" ]; then
    url_count=$(wc -l < urls.txt)
    echo -e "${GREEN}✅ urls.txt найден ($url_count URL-ов)${NC}"
else
    echo -e "${YELLOW}⚠️  urls.txt не найден${NC}"
    echo -e "${BLUE}📝 Создаем пример файла...${NC}"
    
    cat > urls.txt.example << 'EOF'
https://example.com/page1
https://example.com/page2
https://example.com/page3
EOF
    
    echo -e "${YELLOW}📝 Создан пример urls.txt.example${NC}"
    echo -e "${BLUE}📖 Скопируйте urls.txt.example в urls.txt и добавьте ваши URL-ы${NC}"
fi

echo ""

# Шаг 5: Настраиваем права доступа
echo -e "${BLUE}📋 Шаг 5: Настройка прав доступа${NC}"
echo -e "${CYAN}================================${NC}"

# Делаем скрипты исполняемыми
echo -e "${BLUE}🔧 Настраиваем права доступа к скриптам...${NC}"
chmod +x *.command 2>/dev/null
chmod +x *.py 2>/dev/null

echo -e "${GREEN}✅ Права доступа настроены${NC}"

echo ""

# Шаг 6: Тестируем установку
echo -e "${BLUE}📋 Шаг 6: Тестирование установки${NC}"
echo -e "${CYAN}==============================${NC}"

echo -e "${BLUE}🧪 Тестируем Python и зависимости...${NC}"

# Тестируем импорт основных модулей
python3 -c "
import sys
print('✅ Python работает корректно')

try:
    import requests
    print('✅ requests установлен')
except ImportError:
    print('❌ requests не установлен')

try:
    from google.oauth2 import service_account
    print('✅ google-auth установлен')
except ImportError:
    print('❌ google-auth не установлен')

try:
    from google.auth.transport.requests import Request
    print('✅ google-auth-httplib2 установлен')
except ImportError:
    print('❌ google-auth-httplib2 не установлен')
"

echo ""

# Шаг 7: Финальная проверка
echo -e "${BLUE}📋 Шаг 7: Финальная проверка${NC}"
echo -e "${CYAN}============================${NC}"

echo -e "${YELLOW}📄 Проверяем наличие основных файлов:${NC}"

files=("main.py" "check_permissions.py" "setup_service_account.py" "run_indexing.command" "quick_run.command" "check_setup.command")
missing_files=()

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}   ✅ $file${NC}"
    else
        echo -e "${RED}   ❌ $file${NC}"
        missing_files+=("$file")
    fi
done

echo ""

# Результат установки
if [ ${#missing_files[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 Установка завершена успешно!${NC}"
    echo ""
    echo -e "${BLUE}🚀 Для запуска используйте:${NC}"
    echo -e "${BLUE}   • Двойной клик на quick_run.command (быстрый запуск)${NC}"
    echo -e "${BLUE}   • Двойной клик на run_indexing.command (с настройками)${NC}"
    echo -e "${BLUE}   • Двойной клик на check_setup.command (диагностика)${NC}"
    echo ""
    echo -e "${BLUE}📖 Документация:${NC}"
    echo -e "${BLUE}   • README.MD - основная документация${NC}"
    echo -e "${BLUE}   • SEO_GUIDE.md - руководство по SEO${NC}"
else
    echo -e "${YELLOW}⚠️  Установка завершена с предупреждениями${NC}"
    echo -e "${YELLOW}📝 Отсутствуют файлы: ${missing_files[*]}${NC}"
    echo -e "${BLUE}📖 Скачайте полную версию приложения${NC}"
fi

echo ""
echo -e "${PURPLE}🔧 Следующие шаги:${NC}"
echo -e "${PURPLE}   1. Настройте service_account.json (если не настроен)${NC}"
echo -e "${PURPLE}   2. Добавьте URL-ы в urls.txt${NC}"
echo -e "${PURPLE}   3. Запустите check_setup.command для диагностики${NC}"

echo ""
read -p "Нажмите Enter для завершения установки..." 