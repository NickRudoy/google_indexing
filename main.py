#!/usr/bin/env python3
"""
Google Indexing API Bulk Tool
Инструмент для массовой отправки URL-ов в Google Indexing API
"""

import json
import os
import sys
import time
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import argparse
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Установите зависимости: pip install google-auth google-auth-oauthlib google-auth-httplib2 requests")
    sys.exit(1)


class GoogleIndexingBulk:
    """Класс для работы с Google Indexing API"""
    
    def __init__(self, service_account_path: str = "service_account.json"):
        """
        Инициализация с файлом сервисного аккаунта
        
        Args:
            service_account_path: Путь к файлу service_account.json
        """
        self.service_account_path = Path(service_account_path)
        self.credentials = None
        self.access_token = None
        self.service_account_email = None
        
        if not self.service_account_path.exists():
            raise FileNotFoundError(f"Файл {service_account_path} не найден!")
        
        self._authenticate()
        self._setup_logging()
    
    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('indexing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _authenticate(self):
        """Аутентификация через сервисный аккаунт"""
        try:
            # Загружаем учетные данные из файла
            with open(self.service_account_path, 'r') as f:
                service_account_data = json.load(f)
            
            self.service_account_email = service_account_data.get('client_email')
            if not self.service_account_email:
                raise ValueError("Email сервисного аккаунта не найден в JSON файле")
            
            self.credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=['https://www.googleapis.com/auth/indexing']
            )
            
            # Получаем токен доступа
            self.credentials.refresh(Request())
            self.access_token = self.credentials.token
            
            print("✅ Аутентификация успешна!")
            print(f"📧 Сервисный аккаунт: {self.service_account_email}")
            
        except Exception as e:
            print(f"❌ Ошибка аутентификации: {e}")
            raise
    
    def check_domain_ownership(self, urls: List[str]) -> Dict[str, List[str]]:
        """
        Проверка владения доменами
        
        Args:
            urls: Список URL-ов для проверки
        
        Returns:
            Словарь с доменами и их статусом
        """
        domains = {}
        for url in urls:
            domain = urlparse(url).netloc
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(url)
        
        print(f"\n🔍 Проверяем владение доменами...")
        print(f"📧 Убедитесь, что {self.service_account_email} добавлен как владелец в Search Console для:")
        
        for domain in domains:
            print(f"   - {domain}")
        
        return domains
    
    def submit_urls(self, urls: List[str], batch_size: int = 100, max_retries: int = 3) -> Dict:
        """
        Отправка URL-ов в Google Indexing API
        
        Args:
            urls: Список URL-ов для отправки
            batch_size: Размер пакета (максимум 100)
            max_retries: Максимальное количество попыток
        
        Returns:
            Словарь с результатами отправки
        """
        if not urls:
            return {"success": False, "message": "Список URL-ов пуст"}
        
        # Проверяем владение доменами
        self.check_domain_ownership(urls)
        
        # Ограничиваем размер пакета
        batch_size = min(batch_size, 100)
        
        results = {
            "total_urls": len(urls),
            "batches": [],
            "success_count": 0,
            "error_count": 0,
            "errors": [],
            "domain_stats": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Разбиваем на пакеты
        batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
        
        print(f"\n📦 Отправляем {len(urls)} URL-ов в {len(batches)} пакетах...")
        
        for i, batch in enumerate(batches, 1):
            print(f"   Пакет {i}/{len(batches)} ({len(batch)} URL-ов)...")
            
            batch_result = self._submit_batch_with_retry(batch, max_retries)
            results["batches"].append(batch_result)
            
            if batch_result["success"]:
                results["success_count"] += len(batch)
            else:
                results["error_count"] += len(batch)
                results["errors"].extend(batch_result.get("errors", []))
            
            # Небольшая пауза между пакетами
            if i < len(batches):
                time.sleep(2)
        
        # Анализируем статистику по доменам
        results["domain_stats"] = self._analyze_domain_stats(urls, results)
        
        return results
    
    def _submit_batch_with_retry(self, urls: List[str], max_retries: int) -> Dict:
        """
        Отправка пакета с повторными попытками
        
        Args:
            urls: Список URL-ов для пакета
            max_retries: Максимальное количество попыток
        
        Returns:
            Результат отправки пакета
        """
        for attempt in range(max_retries):
            try:
                result = self._submit_batch(urls)
                
                if result["success"]:
                    return result
                
                # Проверяем, стоит ли повторять
                if "403" in result.get("error", "") and "ownership" in result.get("error", "").lower():
                    print(f"   ⚠️  Ошибка прав доступа (попытка {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))  # Увеличиваем задержку
                        continue
                
                return result
                
            except Exception as e:
                error_msg = f"Ошибка в попытке {attempt + 1}: {e}"
                print(f"   ❌ {error_msg}")
                
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                
                return {
                    "success": False,
                    "urls_count": len(urls),
                    "error": error_msg
                }
        
        return {
            "success": False,
            "urls_count": len(urls),
            "error": "Превышено максимальное количество попыток"
        }
    
    def _submit_batch(self, urls: List[str]) -> Dict:
        """
        Отправка одного пакета URL-ов
        
        Args:
            urls: Список URL-ов для пакета
        
        Returns:
            Результат отправки пакета
        """
        # Формируем multipart данные
        boundary = f"batch_{int(time.time())}"
        headers = {
            'Content-Type': f'multipart/mixed; boundary={boundary}',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        body_parts = []
        
        for url in urls:
            # Формируем часть для каждого URL
            part_boundary = f"--{boundary}"
            content_id = f"<{int(time.time() * 1000)}>"
            
            # HTTP заголовки
            http_headers = (
                f"POST /v3/urlNotifications:publish HTTP/1.1\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(json.dumps({'url': url, 'type': 'URL_UPDATED'}))}\r\n\r\n"
            )
            
            # JSON данные
            json_data = json.dumps({
                'url': url,
                'type': 'URL_UPDATED'
            })
            
            # Собираем часть
            part = (
                f"{part_boundary}\r\n"
                f"Content-Type: application/http\r\n"
                f"Content-ID: {content_id}\r\n\r\n"
                f"{http_headers}"
                f"{json_data}\r\n"
            )
            
            body_parts.append(part)
        
        # Закрывающая граница
        body_parts.append(f"--{boundary}--")
        
        # Собираем тело запроса
        body = "\r\n".join(body_parts)
        
        try:
            response = requests.post(
                'https://indexing.googleapis.com/batch',
                headers=headers,
                data=body.encode('utf-8'),
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "urls_count": len(urls),
                    "response": response.text,
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "urls_count": len(urls),
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "urls_count": len(urls),
                "error": str(e)
            }
    
    def _analyze_domain_stats(self, urls: List[str], results: Dict) -> Dict:
        """
        Анализ статистики по доменам
        
        Args:
            urls: Список URL-ов
            results: Результаты отправки
        
        Returns:
            Статистика по доменам
        """
        domain_stats = {}
        
        for url in urls:
            domain = urlparse(url).netloc
            if domain not in domain_stats:
                domain_stats[domain] = {
                    "total_urls": 0,
                    "success_count": 0,
                    "error_count": 0
                }
            domain_stats[domain]["total_urls"] += 1
        
        # Анализируем ошибки по доменам
        for batch in results["batches"]:
            if not batch["success"]:
                # Это упрощенный анализ - в реальности нужно парсить batch response
                pass
        
        return domain_stats


def load_urls_from_file(file_path: str) -> List[str]:
    """
    Загрузка URL-ов из файла
    
    Args:
        file_path: Путь к файлу с URL-ами
    
    Returns:
        Список URL-ов
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден!")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    # Валидация URL-ов
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        if url.startswith(('http://', 'https://')):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    if invalid_urls:
        print(f"⚠️  Найдено {len(invalid_urls)} некорректных URL-ов:")
        for url in invalid_urls[:5]:  # Показываем первые 5
            print(f"   {url}")
        if len(invalid_urls) > 5:
            print(f"   ... и еще {len(invalid_urls) - 5}")
    
    return valid_urls


def save_results(results: Dict, output_file: str = None):
    """
    Сохранение результатов в файл
    
    Args:
        results: Результаты отправки
        output_file: Путь к файлу для сохранения
    """
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"indexing_results_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Результаты сохранены в {output_file}")


def print_detailed_results(results: Dict):
    """
    Вывод детальных результатов
    
    Args:
        results: Результаты отправки
    """
    print("\n" + "="*60)
    print("📊 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ ОТПРАВКИ")
    print("="*60)
    print(f"Всего URL-ов: {results['total_urls']}")
    print(f"Успешно отправлено: {results['success_count']}")
    print(f"Ошибок: {results['error_count']}")
    print(f"Пакетов: {len(results['batches'])}")
    print(f"Время выполнения: {results.get('timestamp', 'N/A')}")
    
    # Статистика по доменам
    if results.get('domain_stats'):
        print(f"\n🌐 Статистика по доменам:")
        for domain, stats in results['domain_stats'].items():
            print(f"   {domain}: {stats['total_urls']} URL-ов")
    
    # Анализ ошибок
    if results['errors']:
        print(f"\n❌ Основные ошибки:")
        error_types = {}
        for error in results['errors']:
            if "403" in error and "ownership" in error.lower():
                error_types["Права доступа"] = error_types.get("Права доступа", 0) + 1
            elif "429" in error:
                error_types["Превышен лимит"] = error_types.get("Превышен лимит", 0) + 1
            else:
                error_types["Другие ошибки"] = error_types.get("Другие ошибки", 0) + 1
        
        for error_type, count in error_types.items():
            print(f"   {error_type}: {count}")
    
    # Рекомендации
    print(f"\n💡 Рекомендации:")
    if results['error_count'] > 0:
        print("   1. Проверьте права доступа сервисного аккаунта в Search Console")
        print("   2. Убедитесь, что домены добавлены в Search Console")
        print("   3. Проверьте валидность URL-ов")
    else:
        print("   ✅ Все URL-ы успешно отправлены!")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Google Indexing API Bulk Tool - Массовая отправка URL-ов для индексации",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py urls.txt
  python main.py urls.txt --batch-size 50
  python main.py urls.txt --service-account my_account.json
  python main.py urls.txt --save-results
  python main.py urls.txt --max-retries 5
        """
    )
    
    parser.add_argument(
        'urls_file',
        help='Файл с URL-ами (по одному на строку)'
    )
    
    parser.add_argument(
        '--service-account',
        default='service_account.json',
        help='Путь к файлу service_account.json (по умолчанию: service_account.json)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Размер пакета (максимум 100, по умолчанию: 100)'
    )
    
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Максимальное количество попыток (по умолчанию: 3)'
    )
    
    parser.add_argument(
        '--save-results',
        action='store_true',
        help='Сохранить результаты в JSON файл'
    )
    
    parser.add_argument(
        '--output-file',
        help='Имя файла для сохранения результатов'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Подробный вывод'
    )
    
    args = parser.parse_args()
    
    try:
        # Загружаем URL-ы
        print(f"📁 Загружаем URL-ы из {args.urls_file}...")
        urls = load_urls_from_file(args.urls_file)
        
        if not urls:
            print("❌ Не найдено валидных URL-ов!")
            return
        
        print(f"✅ Загружено {len(urls)} валидных URL-ов")
        
        # Инициализируем API
        print("🔐 Инициализируем Google Indexing API...")
        api = GoogleIndexingBulk(args.service_account)
        
        # Отправляем URL-ы
        results = api.submit_urls(urls, args.batch_size, args.max_retries)
        
        # Выводим детальные результаты
        print_detailed_results(results)
        
        # Сохраняем результаты если нужно
        if args.save_results or args.output_file:
            save_results(results, args.output_file)
        
        print("\n✅ Готово!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()