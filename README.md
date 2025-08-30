# SEO Audit Tool

Комплексный инструмент для анализа SEO оптимизации сайтов с подробными отчетами и рекомендациями.

## 🚀 Быстрый старт

### Локальный запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd seo-audit-tool
   ```

2. **Настройте виртуальное окружение:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите приложение:**
   ```bash
   # Режим разработки
   FLASK_ENV=development python src/app/__init__.py

   # или через gunicorn (продакшн)
   gunicorn --bind 0.0.0.0:5000 src.app:app
   ```

5. **Откройте в браузере:**
   ```
   http://localhost:5000
   ```

## 📋 Возможности

### Анализ SEO параметров
- ✅ **Мета-теги** - title, description, keywords
- ✅ **Производительность** - скорость загрузки, размер страниц
- ✅ **Структура ссылок** - внутренние/внешние ссылки
- ✅ **Мобильная адаптивность** - viewport, responsive design
- ✅ **SSL безопасность** - сертификаты, HTTPS
- ✅ **Контент анализ** - качество текста, заголовки

### Отчеты и рекомендации
- 📊 **Визуальные оценки** - цветовые индикаторы качества
- 📋 **Детальные рекомендации** - конкретные советы по улучшению
- 📤 **Экспорт результатов** - JSON, PDF (в будущем)
- 🎯 **Приоритизация** - критичные, средние, низкие проблемы

## 🏗️ Архитектура

```
seo-audit-tool/
├── src/
│   ├── app/               # Flask приложение
│   ├── seo_analyzer/      # Модуль анализа
│   └── reports/          # Генерация отчетов
├── templates/            # HTML шаблоны
├── static/              # CSS, JS, изображения
├── docs/               # Документация
└── .cursor/rules/      # Правила разработки
```

## 🐳 Развертывание на DigitalOcean

### Вариант 1: DO App Platform (Рекомендуемый)

#### Шаг 1: Подготовка репозитория
```bash
# Код уже загружен на GitHub
git clone https://github.com/teamhubbel-max/DOteamcrn.git
cd DOteamcrn
```

#### Шаг 2: Развертывание через DO App Platform
1. Перейдите в [DO App Platform](https://cloud.digitalocean.com/apps)
2. Выберите "Create App" → "GitHub"
3. Подключите ваш GitHub аккаунт и выберите репозиторий
4. Выберите ветку `main`
5. DO автоматически обнаружит `app-spec.yaml`
6. Установите переменные окружения:
   - `SECRET_KEY`: Сгенерируйте случайную строку
   - `FLASK_ENV`: `production`

#### Шаг 3: Настройка домена (опционально)
1. В настройках приложения перейдите в "Settings" → "Domains"
2. Добавьте ваш домен или используйте предоставленный DO

### Вариант 2: DO Droplets + Docker

#### Шаг 1: Создание Droplet
```bash
# Создайте Ubuntu Droplet через DO панель
# Рекомендуемые характеристики:
# - Ubuntu 22.04
# - 1GB RAM минимум
# - 25GB диск
```

#### Шаг 2: Установка Docker
```bash
# Подключитесь к Droplet по SSH
ssh root@YOUR_DROPLET_IP

# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### Шаг 3: Развертывание приложения
```bash
# Клонируйте репозиторий
git clone https://github.com/teamhubbel-max/DOteamcrn.git
cd DOteamcrn

# Соберите Docker образ
docker build -t seo-audit-tool .

# Запустите контейнер
docker run -d \
  --name seo-audit-app \
  -p 80:5000 \
  -e SECRET_KEY="your-secret-key-here" \
  -e FLASK_ENV="production" \
  seo-audit-tool
```

#### Шаг 4: Настройка Nginx (опционально)
```bash
# Установите Nginx
sudo apt update
sudo apt install nginx

# Создайте конфигурацию
sudo nano /etc/nginx/sites-available/seo-audit
```

Добавьте в файл:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Активируйте конфигурацию
sudo ln -s /etc/nginx/sites-available/seo-audit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Переменные окружения

Создайте файл `.env` в корне проекта:

```bash
# Секретный ключ Flask (генерируйте случайную строку)
SECRET_KEY=your-super-secret-key-here-change-this-in-production

# Среда выполнения
FLASK_ENV=production

# Настройки анализа
MAX_ANALYSIS_TIME=30
MAX_URLS_PER_ANALYSIS=10

# Для DO App Platform
DO_APP=true
```

## 🚀 Быстрый старт развертывания

### Использование скрипта развертывания
```bash
# Для локального тестирования Docker
./deploy.sh local

# Для развертывания на DO (требует doctl)
./deploy.sh do

# Только сборка Docker образа
./deploy.sh docker
```

### Ручное развертывание

#### Локально с Docker
```bash
# 1. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env файл

# 2. Соберите и запустите
docker build -t seo-audit-tool .
docker run -d --name seo-audit-app -p 5000:5000 --env-file .env seo-audit-tool
```

#### На DO App Platform
```bash
# 1. Загрузите код на GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Создайте приложение через DO панель или doctl
doctl apps create app-spec.yaml
```

## 🎯 Использование приложения

### Веб-интерфейс
1. Откройте приложение в браузере
2. Введите URL сайта для анализа
3. Нажмите "Начать анализ"
4. Получите подробный отчет

### API
```bash
# Анализ сайта
curl -X POST http://your-domain.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Проверка здоровья
curl http://your-domain.com/health
```

## 🔍 Возможности анализа

- ✅ **Мета-теги** (title, description, keywords)
- ✅ **Производительность** (скорость загрузки)
- ✅ **Структура ссылок** (внутренние/внешние)
- ✅ **Мобильная адаптивность**
- ✅ **SSL сертификаты**
- ✅ **Контент анализ**

## 📊 Примеры отчетов

Приложение генерирует подробные отчеты с:
- Общей оценкой SEO (0-100 баллов)
- Детальными рекомендациями
- Визуальными графиками
- Предложениями по улучшению

---

**SEO Audit Tool** готов к развертыванию на DigitalOcean! 🚀

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `FLASK_ENV` | Среда выполнения | development |
| `SECRET_KEY` | Секретный ключ Flask | dev-secret-key |
| `MAX_ANALYSIS_TIME` | Макс. время анализа (сек) | 30 |
| `MAX_URLS_PER_ANALYSIS` | Макс. URL за анализ | 10 |
| `PORT` | Порт сервера | 5000 |

### Кастомизация

- **Шаблоны:** `templates/` - HTML файлы
- **Стили:** `static/css/` - CSS файлы
- **JavaScript:** `static/js/` - клиентские скрипты
- **Анализаторы:** `src/seo_analyzer/` - логика анализа

## 📊 API

### Анализ сайта
```http
POST /api/analyze
Content-Type: application/json

{
  "url": "https://example.com"
}
```

**Ответ:**
```json
{
  "success": true,
  "url": "https://example.com",
  "analysis": {
    "status": "completed",
    "analysis_time": 2.34,
    "results": {
      "meta": {...},
      "performance": {...},
      "links": {...}
    }
  }
}
```

### Проверка здоровья
```http
GET /health
```

## 🧪 Тестирование

### Запуск тестов
```bash
# Модульные тесты
python -m pytest tests/unit/

# Интеграционные тесты
python -m pytest tests/integration/

# Все тесты
python -m pytest
```

### Добавление тестов
```python
# tests/unit/test_seo_analyzer.py
def test_meta_analysis():
    analyzer = SEOAnalyzer()
    # Ваш тест
```

## 📚 Документация

- **Project.md** - архитектура и дизайн
- **changelog.md** - история изменений
- **tasktracker.md** - текущие задачи

## 🤝 Разработка

### Code Style
- **Black** - форматирование кода
- **Flake8** - линтинг
- **MyPy** - типизация

### Pre-commit hooks
```bash
pip install pre-commit
pre-commit install
```

### Cursor Rules
Проект использует структурированные правила разработки в `.cursor/rules/`

## 📄 Лицензия

MIT License - см. файл LICENSE

## 👥 Команда

- **Разработчик:** AI Assistant
- **Архитектор:** AI Assistant
- **Тестировщик:** AI Assistant

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Создайте issue в репозитории
3. Свяжитесь с командой разработчиков

---

**SEO Audit Tool** - ваш надежный помощник в оптимизации сайтов! 🚀
