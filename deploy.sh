#!/bin/bash

# SEO Audit Tool - Скрипт развертывания
# Использование: ./deploy.sh [local|do|docker]

set -e

PROJECT_NAME="seo-audit-tool"
DOCKER_IMAGE="${PROJECT_NAME}:latest"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции логирования
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
}

# Проверка наличия doctl
check_doctl() {
    if ! command -v doctl &> /dev/null; then
        log_error "doctl не установлен. Установите doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi
}

# Локальное развертывание с Docker
deploy_local() {
    log_info "🚀 Начинаем локальное развертывание с Docker..."

    check_docker

    # Проверяем наличие .env файла
    if [ ! -f .env ]; then
        log_warning ".env файл не найден. Создаем из .env.example..."
        cp .env.example .env
        log_warning "Отредактируйте .env файл перед запуском!"
    fi

    # Собираем образ
    log_info "📦 Собираем Docker образ..."
    docker build -t $DOCKER_IMAGE .

    # Останавливаем и удаляем старый контейнер
    log_info "🧹 Очищаем старые контейнеры..."
    docker stop $PROJECT_NAME 2>/dev/null || true
    docker rm $PROJECT_NAME 2>/dev/null || true

    # Запускаем новый контейнер
    log_info "🐳 Запускаем контейнер..."
    docker run -d \
        --name $PROJECT_NAME \
        -p 5000:5000 \
        --env-file .env \
        $DOCKER_IMAGE

    # Ждем запуска
    log_info "⏳ Ждем запуска приложения..."
    sleep 5

    # Проверяем статус
    if docker ps | grep -q $PROJECT_NAME; then
        log_success "✅ Приложение запущено успешно!"
        log_info "🌐 Доступно по адресу: http://localhost:5000"
        log_info "📊 API доступен: http://localhost:5000/api/analyze"
        log_info "💚 Health check: http://localhost:5000/health"
    else
        log_error "❌ Ошибка запуска контейнера"
        log_info "📋 Логи контейнера:"
        docker logs $PROJECT_NAME
        exit 1
    fi
}

# Развертывание на DigitalOcean App Platform
deploy_do() {
    log_info "🌊 Начинаем развертывание на DigitalOcean App Platform..."

    check_doctl

    # Проверяем наличие app-spec.yaml
    if [ ! -f app-spec.yaml ]; then
        log_error "app-spec.yaml не найден!"
        exit 1
    fi

    # Проверяем авторизацию в DO
    if ! doctl account get &> /dev/null; then
        log_error "doctl не авторизован. Выполните: doctl auth init"
        exit 1
    fi

    log_info "📦 Создаем приложение на DO App Platform..."
    APP_ID=$(doctl apps create app-spec.yaml --format ID --no-header 2>/dev/null || true)

    if [ -z "$APP_ID" ]; then
        log_error "❌ Ошибка создания приложения"
        log_info "Возможные причины:"
        log_info "1. Проверьте app-spec.yaml"
        log_info "2. Проверьте подключение к GitHub"
        log_info "3. Проверьте квоту на DO аккаунте"
        exit 1
    fi

    log_success "✅ Приложение создано! ID: $APP_ID"
    log_info "📊 Статус развертывания можно проверить в DO панели"
    log_info "🔗 URL появится после завершения развертывания"
}

# Сборка только Docker образа
build_docker() {
    log_info "🔨 Собираем Docker образ..."

    check_docker

    docker build -t $DOCKER_IMAGE .
    log_success "✅ Docker образ собран: $DOCKER_IMAGE"
}

# Показать справку
show_help() {
    echo "SEO Audit Tool - Скрипт развертывания"
    echo ""
    echo "Использование:"
    echo "  $0 local    - Локальное развертывание с Docker"
    echo "  $0 do       - Развертывание на DO App Platform"
    echo "  $0 docker   - Только сборка Docker образа"
    echo "  $0 help     - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 local"
    echo "  $0 do"
}

# Основная логика
case "${1:-help}" in
    "local")
        deploy_local
        ;;
    "do")
        deploy_do
        ;;
    "docker")
        build_docker
        ;;
    "help"|*)
        show_help
        ;;
esac
