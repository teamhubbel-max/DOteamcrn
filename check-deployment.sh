#!/bin/bash

# Скрипт для проверки статуса развертывания DO App Platform
# Использование: ./check-deployment.sh [app-name]

APP_NAME=${1:-"doteamcrn"}
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Проверка статуса развертывания: $APP_NAME${NC}"
echo "=================================================="

# Функция для проверки доступности DO CLI
check_doctl() {
    if command -v doctl &> /dev/null; then
        echo -e "${GREEN}✅ DO CLI установлен${NC}"
        return 0
    else
        echo -e "${RED}❌ DO CLI не установлен${NC}"
        echo -e "${YELLOW}Установите DO CLI: https://docs.digitalocean.com/reference/doctl/how-to/install/${NC}"
        return 1
    fi
}

# Функция для проверки аутентификации
check_auth() {
    if doctl account get &> /dev/null; then
        echo -e "${GREEN}✅ Аутентификация DO CLI успешна${NC}"
        return 0
    else
        echo -e "${RED}❌ Аутентификация DO CLI не настроена${NC}"
        echo -e "${YELLOW}Выполните: doctl auth init${NC}"
        return 1
    fi
}

# Функция для получения информации о приложении
get_app_info() {
    echo -e "\n${YELLOW}📱 Информация о приложении:${NC}"

    # Получить список приложений
    APPS=$(doctl apps list --format ID,Name,Phase,UpdatedAt --no-header 2>/dev/null)

    if [ $? -eq 0 ] && [ ! -z "$APPS" ]; then
        echo "$APPS" | while read -r app_id app_name phase updated; do
            if [[ "$app_name" == *"$APP_NAME"* ]] || [[ "$app_id" == *"$APP_NAME"* ]]; then
                echo -e "ID: ${GREEN}$app_id${NC}"
                echo -e "Имя: ${GREEN}$app_name${NC}"
                echo -e "Статус: ${GREEN}$phase${NC}"
                echo -e "Обновлено: ${GREEN}$updated${NC}"
                return 0
            fi
        done
    fi

    echo -e "${RED}❌ Приложение '$APP_NAME' не найдено${NC}"
    return 1
}

# Функция для получения информации о развертывании
get_deployment_info() {
    echo -e "\n${YELLOW}🚀 Информация о развертывании:${NC}"

    # Найти приложение по имени
    APP_ID=$(doctl apps list --format ID,Name --no-header 2>/dev/null | grep "$APP_NAME" | head -1 | awk '{print $1}')

    if [ -z "$APP_ID" ]; then
        echo -e "${RED}❌ Не удалось найти ID приложения${NC}"
        return 1
    fi

    # Получить информацию о развертываниях
    DEPLOYMENTS=$(doctl apps list-deployments "$APP_ID" --format ID,Phase,Cause,CreatedAt --no-header 2>/dev/null | head -5)

    if [ $? -eq 0 ] && [ ! -z "$DEPLOYMENTS" ]; then
        echo "$DEPLOYMENTS" | while read -r dep_id phase cause created; do
            echo -e "Развертывание: ${GREEN}$dep_id${NC}"
            echo -e "Статус: ${GREEN}$phase${NC}"
            echo -e "Причина: ${GREEN}$cause${NC}"
            echo -e "Создано: ${GREEN}$created${NC}"
            echo "---"
        done
    else
        echo -e "${RED}❌ Не удалось получить информацию о развертываниях${NC}"
        return 1
    fi
}

# Функция для получения логов
get_logs() {
    echo -e "\n${YELLOW}📋 Попытка получения логов:${NC}"

    APP_ID=$(doctl apps list --format ID,Name --no-header 2>/dev/null | grep "$APP_NAME" | head -1 | awk '{print $1}')

    if [ -z "$APP_ID" ]; then
        echo -e "${RED}❌ Не удалось найти ID приложения${NC}"
        return 1
    fi

    echo -e "${YELLOW}Получение логов для приложения $APP_ID...${NC}"

    # Попытаться получить логи с таймаутом
    timeout 30 doctl apps logs "$APP_ID" --follow 2>/dev/null || {
        echo -e "${RED}❌ Ошибка получения логов. Возможно, кластер еще не готов.${NC}"
        return 1
    }
}

# Основная логика
main() {
    # Проверка DO CLI
    if ! check_doctl; then
        echo -e "\n${YELLOW}💡 Альтернативные способы проверки:${NC}"
        echo "1. Проверьте статус в веб-интерфейсе DO App Platform"
        echo "2. Подождите 5-10 минут после создания/обновления приложения"
        echo "3. Попробуйте перезагрузить страницу DO App Platform"
        echo "4. Проверьте статус компонентов в DO Status: https://status.digitalocean.com/"
        exit 1
    fi

    # Проверка аутентификации
    if ! check_auth; then
        exit 1
    fi

    # Получение информации о приложении
    if ! get_app_info; then
        exit 1
    fi

    # Получение информации о развертывании
    get_deployment_info

    # Попытка получения логов
    echo -e "\n${YELLOW}⏳ Ожидание готовности кластера...${NC}"
    sleep 3

    if get_logs; then
        echo -e "\n${GREEN}✅ Логи успешно получены!${NC}"
    else
        echo -e "\n${YELLOW}⚠️  Советы по устранению проблемы:${NC}"
        echo "1. Подождите еще 5-10 минут"
        echo "2. Проверьте статус в DO App Platform веб-интерфейсе"
        echo "3. Попробуйте force rebuild приложения"
        echo "4. Проверьте логи билда в разделе 'Deployments'"
        echo "5. Убедитесь, что приложение не в состоянии 'Suspended'"
    fi
}

# Запуск основной функции
main "$@"
