#!/usr/bin/env python3
"""
Скрипт для настройки сервисного аккаунта Google Indexing API
"""

import json
import sys
from pathlib import Path

try:
    from google.cloud import iam_admin_v1
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Установите зависимости: pip install google-cloud-iam")
    sys.exit(1)


def check_service_account_file(file_path: str = "service_account.json"):
    """
    Проверка файла сервисного аккаунта
    
    Args:
        file_path: Путь к файлу service_account.json
    """
    print("🔍 Проверяем файл сервисного аккаунта...")
    
    if not Path(file_path).exists():
        print(f"❌ Файл {file_path} не найден!")
        return None
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"❌ Отсутствуют обязательные поля: {missing_fields}")
            return None
        
        print("✅ Файл сервисного аккаунта корректен")
        print(f"📧 Email: {data['client_email']}")
        print(f"🏗️  Project ID: {data['project_id']}")
        
        return data
        
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return None


def test_indexing_api_access(service_account_path: str = "service_account.json"):
    """
    Тестирование доступа к Indexing API
    
    Args:
        service_account_path: Путь к файлу service_account.json
    """
    print("\n🧪 Тестируем доступ к Indexing API...")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/indexing']
        )
        credentials.refresh(Request())
        
        print("✅ Аутентификация успешна")
        print(f"📧 Сервисный аккаунт: {credentials.service_account_email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка аутентификации: {e}")
        return False


def print_setup_instructions():
    """
    Вывод инструкций по настройке
    """
    print("\n" + "="*60)
    print("📋 ИНСТРУКЦИИ ПО НАСТРОЙКЕ СЕРВИСНОГО АККАУНТА")
    print("="*60)
    
    print("\n1️⃣ Создание сервисного аккаунта:")
    print("   • Зайдите в https://console.cloud.google.com/")
    print("   • Выберите проект (или создайте новый)")
    print("   • Перейдите в IAM & Admin → Service Accounts")
    print("   • Нажмите Create Service Account")
    print("   • Имя: indexing-api-service")
    print("   • Описание: Service account for Google Indexing API")
    
    print("\n2️⃣ Настройка ролей:")
    print("   • Нажмите Continue")
    print("   • Добавьте роль: Service Account User")
    print("   • Нажмите Done")
    
    print("\n3️⃣ Создание ключа:")
    print("   • Нажмите на созданный сервисный аккаунт")
    print("   • Перейдите на вкладку Keys")
    print("   • Нажмите Add Key → Create new key")
    print("   • Выберите JSON")
    print("   • Скачайте файл и переименуйте в service_account.json")
    
    print("\n4️⃣ Включение Indexing API:")
    print("   • В Google Cloud Console перейдите в APIs & Services → Library")
    print("   • Найдите Indexing API")
    print("   • Нажмите Enable")
    
    print("\n5️⃣ Добавление в Search Console:")
    print("   • Зайдите в https://search.google.com/search-console")
    print("   • Войдите под rbru.org@gmail.com")
    print("   • Выберите домен mmcake.ru")
    print("   • Перейдите в Settings → Owners")
    print("   • Нажмите Add Owner")
    print("   • Введите email сервисного аккаунта (из JSON файла)")
    print("   • Подтвердите добавление")
    
    print("\n6️⃣ Проверка настройки:")
    print("   • Запустите: python check_permissions.py")
    print("   • Протестируйте: python check_permissions.py --test-url https://mmcake.ru/")


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Настройка сервисного аккаунта для Google Indexing API"
    )
    
    parser.add_argument(
        '--service-account',
        default='service_account.json',
        help='Путь к файлу service_account.json'
    )
    
    parser.add_argument(
        '--setup-instructions',
        action='store_true',
        help='Показать инструкции по настройке'
    )
    
    args = parser.parse_args()
    
    if args.setup_instructions:
        print_setup_instructions()
        return
    
    print("🔧 Настройка сервисного аккаунта Google Indexing API")
    print("="*60)
    
    # Проверяем файл сервисного аккаунта
    account_data = check_service_account_file(args.service_account)
    
    if not account_data:
        print("\n❌ Файл сервисного аккаунта не найден или некорректен!")
        print_setup_instructions()
        return
    
    # Тестируем доступ к API
    if test_indexing_api_access(args.service_account):
        print("\n✅ Сервисный аккаунт настроен корректно!")
        print(f"\n📧 Email для добавления в Search Console: {account_data['client_email']}")
        
        print(f"\n🔧 Следующие шаги:")
        print(f"   1. Добавьте {account_data['client_email']} как владельца в Search Console")
        print(f"   2. Запустите: python check_permissions.py")
        print(f"   3. Протестируйте: python check_permissions.py --test-url https://mmcake.ru/")
        
    else:
        print("\n❌ Проблемы с доступом к API!")
        print_setup_instructions()


if __name__ == "__main__":
    main() 