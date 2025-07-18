#!/usr/bin/env python3
"""
Скрипт для проверки прав доступа сервисного аккаунта
"""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Установите зависимости: pip install google-auth google-auth-oauthlib google-auth-httplib2 requests")
    sys.exit(1)


def check_service_account(service_account_path: str = "service_account.json"):
    """
    Проверка сервисного аккаунта
    
    Args:
        service_account_path: Путь к файлу service_account.json
    """
    print("🔍 Проверка сервисного аккаунта...")
    
    # Загружаем данные сервисного аккаунта
    with open(service_account_path, 'r') as f:
        service_account_data = json.load(f)
    
    email = service_account_data.get('client_email')
    project_id = service_account_data.get('project_id')
    
    print(f"📧 Email: {email}")
    print(f"🏗️  Project ID: {project_id}")
    
    # Проверяем аутентификацию
    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/indexing']
        )
        credentials.refresh(Request())
        print("✅ Аутентификация успешна")
    except Exception as e:
        print(f"❌ Ошибка аутентификации: {e}")
        return False
    
    return True


def test_single_url(url: str, service_account_path: str = "service_account.json"):
    """
    Тестирование отправки одного URL
    
    Args:
        url: URL для тестирования
        service_account_path: Путь к файлу service_account.json
    """
    print(f"\n🧪 Тестируем отправку URL: {url}")
    
    try:
        # Аутентификация
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/indexing']
        )
        credentials.refresh(Request())
        access_token = credentials.token
        
        # Отправляем запрос
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        data = {
            'url': url,
            'type': 'URL_UPDATED'
        }
        
        response = requests.post(
            'https://indexing.googleapis.com/v3/urlNotifications:publish',
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ URL успешно отправлен!")
            print(f"   Notification metadata: {result.get('urlNotificationMetadata', {})}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"   Ответ: {response.text}")
            
            # Анализируем ошибку
            if response.status_code == 403:
                print("\n💡 Возможные причины ошибки 403:")
                print("   1. Сервисный аккаунт не добавлен как владелец в Search Console")
                print("   2. Домен не добавлен в Search Console")
                print("   3. Неверный формат URL")
                
                domain = urlparse(url).netloc
                print(f"\n🔧 Для исправления:")
                print(f"   1. Зайдите в https://search.google.com/search-console")
                print(f"   2. Добавьте домен {domain} (если не добавлен)")
                print(f"   3. Добавьте {credentials.service_account_email} как владельца")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False


def check_urls_from_file(urls_file: str, service_account_path: str = "service_account.json"):
    """
    Проверка URL-ов из файла
    
    Args:
        urls_file: Файл с URL-ами
        service_account_path: Путь к файлу service_account.json
    """
    print(f"📁 Проверяем URL-ы из файла: {urls_file}")
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    # Группируем по доменам
    domains = {}
    for url in urls:
        domain = urlparse(url).netloc
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(url)
    
    print(f"\n🌐 Найдено доменов: {len(domains)}")
    for domain, domain_urls in domains.items():
        print(f"   {domain}: {len(domain_urls)} URL-ов")
    
    # Тестируем первый URL каждого домена
    print(f"\n🧪 Тестируем по одному URL с каждого домена...")
    
    success_count = 0
    total_count = 0
    
    for domain, domain_urls in domains.items():
        test_url = domain_urls[0]
        print(f"\n--- Тестируем {domain} ---")
        
        if test_single_url(test_url, service_account_path):
            success_count += 1
        total_count += 1
    
    print(f"\n📊 Результаты тестирования:")
    print(f"   Успешно: {success_count}/{total_count}")
    print(f"   Неудачно: {total_count - success_count}/{total_count}")
    
    if success_count == 0:
        print(f"\n❌ Все тесты неудачны. Проверьте права доступа!")
    elif success_count < total_count:
        print(f"\n⚠️  Частично успешно. Проверьте права для неудачных доменов.")
    else:
        print(f"\n✅ Все тесты успешны! Можно отправлять все URL-ы.")


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Проверка прав доступа сервисного аккаунта для Google Indexing API"
    )
    
    parser.add_argument(
        '--service-account',
        default='service_account.json',
        help='Путь к файлу service_account.json'
    )
    
    parser.add_argument(
        '--urls-file',
        help='Файл с URL-ами для тестирования'
    )
    
    parser.add_argument(
        '--test-url',
        help='Один URL для тестирования'
    )
    
    args = parser.parse_args()
    
    try:
        # Проверяем сервисный аккаунт
        if not check_service_account(args.service_account):
            sys.exit(1)
        
        # Тестируем URL-ы
        if args.test_url:
            test_single_url(args.test_url, args.service_account)
        elif args.urls_file:
            check_urls_from_file(args.urls_file, args.service_account)
        else:
            print("\n💡 Использование:")
            print("   python check_permissions.py --test-url https://example.com")
            print("   python check_permissions.py --urls-file urls.txt")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 