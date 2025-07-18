# 🚀 Google Indexing API - Инструкция по установке

## 📋 Быстрая установка

### Для macOS (рекомендуется)

1. **Скачайте приложение** и распакуйте архив
2. **Двойной клик** на файл `install.command`
3. **Следуйте инструкциям** установщика
4. **Готово!** Приложение настроено автоматически

### Альтернативная установка

Если автоматическая установка не работает, выполните шаги вручную:

## 🔧 Ручная установка

### Шаг 1: Проверка Python

Убедитесь, что у вас установлен Python 3.7 или выше:

```bash
python3 --version
```

Если Python не установлен:
- **macOS**: Скачайте с [python.org](https://python.org)
- **Или установите через Homebrew**: `brew install python`

### Шаг 2: Создание виртуального окружения

```bash
# Перейдите в папку с приложением
cd /path/to/google-index

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

```bash
# Обновите pip
pip install --upgrade pip

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 4: Настройка файлов

1. **Создайте файл `service_account.json`**:
   - Скачайте JSON файл из Google Cloud Console
   - Переименуйте в `service_account.json`
   - Поместите в папку с приложением

2. **Создайте файл `urls.txt`**:
   - Добавьте URL-ы для индексации (по одному на строку)
   - Пример:
     ```
     https://example.com/page1
     https://example.com/page2
     https://example.com/page3
     ```

### Шаг 5: Настройка прав доступа

```bash
# Сделайте скрипты исполняемыми
chmod +x *.command
chmod +x *.py
```

## 🔑 Настройка Google Cloud

### 1. Создание проекта

1. Зайдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Запомните Project ID

### 2. Создание сервисного аккаунта

1. Перейдите в **IAM & Admin** → **Service Accounts**
2. Нажмите **Create Service Account**
3. Имя: `indexing-api-service`
4. Описание: `Service account for Google Indexing API`
5. Нажмите **Continue**

### 3. Настройка ролей

1. Добавьте роль: **Service Account User**
2. Нажмите **Done**

### 4. Создание ключа

1. Нажмите на созданный сервисный аккаунт
2. Перейдите на вкладку **Keys**
3. Нажмите **Add Key** → **Create new key**
4. Выберите **JSON**
5. Скачайте файл и переименуйте в `service_account.json`

### 5. Включение Indexing API

1. В Google Cloud Console перейдите в **APIs & Services** → **Library**
2. Найдите **Indexing API**
3. Нажмите **Enable**

### 6. Добавление в Search Console

1. Зайдите в [Search Console](https://search.google.com/search-console)
2. Выберите ваш домен
3. Перейдите в **Settings** → **Owners**
4. Нажмите **Add Owner**
5. Введите email сервисного аккаунта (из JSON файла)
6. Подтвердите добавление

## 🧪 Проверка установки

Запустите диагностику:

```bash
# Двойной клик на check_setup.command
# Или в терминале:
python3 check_setup.command
```

## 🚀 Запуск приложения

### Быстрый запуск
- **Двойной клик** на `quick_run.command`

### Запуск с настройками
- **Двойной клик** на `run_indexing.command`

### Диагностика
- **Двойной клик** на `check_setup.command`

## 📁 Структура файлов

```
google-index/
├── install.command          # Автоматическая установка
├── quick_run.command        # Быстрый запуск
├── run_indexing.command     # Запуск с настройками
├── check_setup.command      # Диагностика
├── main.py                  # Основной скрипт
├── check_permissions.py     # Проверка прав
├── setup_service_account.py # Настройка аккаунта
├── requirements.txt         # Зависимости
├── service_account.json     # Сервисный аккаунт (создать)
├── urls.txt                 # URL-ы для индексации (создать)
├── venv/                    # Виртуальное окружение (создается)
├── README.MD               # Основная документация
├── SEO_GUIDE.md            # Руководство по SEO
└── INSTALL.md              # Этот файл
```

## ❗ Возможные проблемы

### Ошибка "python: command not found"
- Используйте `python3` вместо `python`
- Убедитесь, что виртуальное окружение активировано

### Ошибка "Permission denied"
- Выполните: `chmod +x *.command`

### Ошибка "Module not found"
- Активируйте виртуальное окружение: `source venv/bin/activate`
- Установите зависимости: `pip install -r requirements.txt`

### Ошибка 403 в API
- Проверьте, что сервисный аккаунт добавлен в Search Console
- Убедитесь, что Indexing API включен в Google Cloud

## 📞 Поддержка

Если у вас возникли проблемы:

1. Запустите `check_setup.command` для диагностики
2. Проверьте логи в `indexing.log`
3. Убедитесь, что все файлы на месте
4. Проверьте настройки Google Cloud

## 🔄 Обновление

Для обновления приложения:

1. Скачайте новую версию
2. Запустите `install.command` заново
3. Выберите "Пересоздать виртуальное окружение" при запросе

---

**Удачной работы с Google Indexing API! 🎉** 