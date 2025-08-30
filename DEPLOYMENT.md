# 🚀 SEO Audit Tool - Руководство по развертыванию

## Быстрый старт

### Предварительные требования

1. **Аккаунт DigitalOcean** ([регистрация](https://cloud.digitalocean.com/registrations/new))
2. **GitHub репозиторий** для хранения кода
3. **Docker** (для локального тестирования)

---

## Метод 1: DigitalOcean App Platform (Рекомендуемый) ⭐

### Шаг 1: Подготовка репозитория

```bash
# Инициализируем Git (если еще не сделали)
git init
git add .
git commit -m "SEO Audit Tool - Ready for deployment"

# Создаем репозиторий на GitHub
# Загружаем код
git remote add origin https://github.com/YOUR_USERNAME/seo-audit-tool.git
git push -u origin main
```

### Шаг 2: Настройка переменных окружения

```bash
# Копируем пример файла
cp .env.example .env

# Генерируем секретный ключ
python3 -c "import secrets; print(secrets.token_hex(32))"
# Вставьте этот ключ в SECRET_KEY в .env файле
```

### Шаг 3: Развертывание на DO App Platform

#### Через веб-интерфейс:
1. Перейдите в [DO App Platform](https://cloud.digitalocean.com/apps)
2. Нажмите **"Create App"**
3. Выберите **GitHub** как источник
4. Подключите ваш GitHub аккаунт
5. Выберите репозиторий `seo-audit-tool`
6. Выберите ветку `main`
7. DO автоматически обнаружит `app-spec.yaml`

#### Настройка переменных окружения:
- `SECRET_KEY`: Ваш секретный ключ
- `FLASK_ENV`: `production`

#### Настройка домена (опционально):
1. В настройках приложения → **Settings** → **Domains**
2. Добавьте ваш домен или используйте предоставленный DO

### Шаг 4: Мониторинг

После развертывания:
- Проверьте статус в DO панели
- Подождите завершения сборки (5-10 минут)
- Получите URL приложения
- Протестируйте: `https://your-app-url/health`

---

## Метод 2: DigitalOcean Droplets + Docker

### Шаг 1: Создание Droplet

```bash
# Рекомендуемые характеристики:
# - Ubuntu 22.04 LTS
# - Regular Intel: 1GB RAM / 1 vCPU / 25GB SSD - $6/месяц
```

### Шаг 2: Подключение к Droplet

```bash
# Подключитесь по SSH
ssh root@YOUR_DROPLET_IP

# Обновите систему
sudo apt update && sudo apt upgrade -y
```

### Шаг 3: Установка Docker

```bash
# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER
# Перезайдите или выполните: newgrp docker
```

### Шаг 4: Развертывание приложения

```bash
# Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/seo-audit-tool.git
cd seo-audit-tool

# Настройте переменные окружения
cp .env.example .env
nano .env  # Отредактируйте переменные

# Соберите Docker образ
docker build -t seo-audit-tool .

# Запустите контейнер
docker run -d \
  --name seo-audit-app \
  -p 80:5000 \
  --env-file .env \
  --restart unless-stopped \
  seo-audit-tool

# Проверьте статус
docker ps
```

### Шаг 5: Настройка Nginx (опционально)

```bash
# Установите Nginx
sudo apt install nginx

# Создайте конфигурацию
sudo nano /etc/nginx/sites-available/seo-audit

# Добавьте:
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

# Активируйте конфигурацию
sudo ln -s /etc/nginx/sites-available/seo-audit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Метод 3: Локальное тестирование

### С помощью Docker Compose

```bash
# Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env файл

# Запустите с Docker Compose
docker-compose up -d

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f
```

### С помощью скрипта развертывания

```bash
# Для локального тестирования
./deploy.sh local

# Или только сборка образа
./deploy.sh docker
```

---

## 🔧 Переменные окружения

Обязательно настройте следующие переменные:

```bash
# Критично для безопасности
SECRET_KEY=your-super-secret-key-here

# Среда выполнения
FLASK_ENV=production  # или development

# Настройки анализа
MAX_ANALYSIS_TIME=30
MAX_URLS_PER_ANALYSIS=10

# Для DO App Platform
DO_APP=true
```

### Генерация SECRET_KEY

```bash
# Python способ
python3 -c "import secrets; print(secrets.token_hex(32))"

# Или используйте онлайн генератор
# https://randomkeygen.com/
```

---

## 🧪 Тестирование развертывания

### Проверка работоспособности

```bash
# Health check
curl https://your-app-url/health

# Ожидаемый ответ:
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-XX..."
}
```

### Тестирование API

```bash
# Тест анализа
curl -X POST https://your-app-url/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

### Тестирование веб-интерфейса

1. Откройте `https://your-app-url` в браузере
2. Введите URL для анализа (например: `google.com`)
3. Нажмите "Начать анализ"
4. Должны получить подробный отчет

---

## 🚨 Устранение неполадок

### Проблема: Приложение не запускается

```bash
# Проверьте логи
docker logs seo-audit-app

# Или для DO App Platform
doctl apps logs <app-id>
```

### Проблема: Ошибка 502/503

```bash
# Проверьте health endpoint
curl https://your-app-url/health

# Перезапустите приложение
docker restart seo-audit-app
```

### Проблема: Таймаут при сборке

- Увеличьте таймаут в DO App Platform
- Проверьте размер репозитория
- Оптимизируйте .dockerignore

---

## 📊 Мониторинг и обслуживание

### DO App Platform
- Автоматическое масштабирование
- Встроенный мониторинг
- Логи в реальном времени
- Автоматические бэкапы

### Droplets
```bash
# Мониторинг ресурсов
htop
docker stats

# Ротация логов
docker logs --since 24h seo-audit-app

# Обновление приложения
docker pull your-registry/seo-audit-tool:latest
docker-compose down
docker-compose up -d
```

---

## 💰 Стоимость

### DO App Platform
- **Basic**: $5/месяц (1 vCPU, 512MB RAM)
- **Professional**: $12/месяц (1 vCPU, 1GB RAM)
- **Бесплатный tier**: 3 месяца

### DO Droplets
- **Basic**: $6/месяц (1 vCPU, 1GB RAM, 25GB SSD)
- **Преимущество**: Полный контроль над сервером

---

## 🎯 Следующие шаги

После успешного развертывания:

1. **Протестируйте** все функции
2. **Настройте мониторинг** (опционально)
3. **Добавьте домен** (рекомендуется)
4. **Настройте бэкапы** (для Droplets)
5. **Оптимизируйте** производительность

---

## 📞 Поддержка

При проблемах:
1. Проверьте логи приложения
2. Изучите документацию DO
3. Создайте issue в репозитории
4. Свяжитесь с поддержкой DO

**Удачного развертывания! 🚀**
