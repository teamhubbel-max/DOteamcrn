#!/usr/bin/env python3
"""
Мониторинг статуса развертывания DO App Platform
Использование: python monitor-deployment.py [app-name]
"""

import requests
import time
import sys
import json
from datetime import datetime
import argparse

class DeploymentMonitor:
    def __init__(self, app_name="doteamcrn", check_interval=30):
        self.app_name = app_name
        self.check_interval = check_interval
        self.api_base = "https://api.digitalocean.com/v2"
        self.session = requests.Session()

        # Цвета для вывода
        self.colors = {
            'green': '\033[0;32m',
            'red': '\033[0;31m',
            'yellow': '\033[1;33m',
            'blue': '\033[0;34m',
            'nc': '\033[0m'  # No Color
        }

    def print_colored(self, text, color='nc'):
        """Вывод цветного текста"""
        print(f"{self.colors.get(color, '')}{text}{self.colors['nc']}")

    def check_app_status(self):
        """Проверка статуса приложения"""
        try:
            # Получить токен из переменных окружения
            token = self.get_do_token()

            if not token:
                self.print_colored("❌ DO_TOKEN не найден. Установите переменную окружения DO_TOKEN", 'red')
                return None

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            # Получить список приложений
            response = self.session.get(f"{self.api_base}/apps", headers=headers, timeout=10)

            if response.status_code == 401:
                self.print_colored("❌ Неверный токен аутентификации", 'red')
                return None
            elif response.status_code != 200:
                self.print_colored(f"❌ Ошибка API: {response.status_code}", 'red')
                return None

            apps = response.json().get('apps', [])

            # Найти приложение по имени
            for app in apps:
                if app['spec']['name'] == self.app_name or app['id'] == self.app_name:
                    return app

            self.print_colored(f"❌ Приложение '{self.app_name}' не найдено", 'red')
            return None

        except requests.exceptions.RequestException as e:
            self.print_colored(f"❌ Ошибка сети: {e}", 'red')
            return None
        except Exception as e:
            self.print_colored(f"❌ Ошибка: {e}", 'red')
            return None

    def check_deployment_status(self, app_id):
        """Проверка статуса развертывания"""
        try:
            token = self.get_do_token()
            if not token:
                return None

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            # Получить deployments
            response = self.session.get(f"{self.api_base}/apps/{app_id}/deployments",
                                     headers=headers, timeout=10)

            if response.status_code == 200:
                deployments = response.json().get('deployments', [])
                if deployments:
                    return deployments[0]  # Последнее развертывание

            return None

        except Exception as e:
            self.print_colored(f"❌ Ошибка получения статуса развертывания: {e}", 'red')
            return None

    def check_app_health(self, app_url):
        """Проверка здоровья приложения"""
        try:
            response = self.session.get(f"{app_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                return health_data
            else:
                return {'status': 'unhealthy', 'code': response.status_code}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def get_do_token(self):
        """Получение DO токена"""
        import os
        return os.getenv('DO_TOKEN')

    def format_timestamp(self, timestamp):
        """Форматирование временной метки"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return timestamp

    def display_app_info(self, app):
        """Отображение информации о приложении"""
        self.print_colored(f"\n📱 ИНФОРМАЦИЯ О ПРИЛОЖЕНИИ: {self.app_name.upper()}", 'blue')
        self.print_colored("=" * 50, 'blue')

        print(f"ID: {app['id']}")
        print(f"Имя: {app['spec']['name']}")
        print(f"Статус: {app['phase']}")
        print(f"Создано: {self.format_timestamp(app['created_at'])}")
        print(f"Обновлено: {self.format_timestamp(app['updated_at'])}")

        if app.get('live_url'):
            print(f"URL: {app['live_url']}")

        if app.get('live_domain'):
            print(f"Домен: {app['live_domain']}")

    def display_deployment_info(self, deployment):
        """Отображение информации о развертывании"""
        if not deployment:
            self.print_colored("\n❌ Информация о развертывании недоступна", 'red')
            return

        self.print_colored("\n🚀 ИНФОРМАЦИЯ О РАЗВЕРТЫВАНИИ", 'blue')
        self.print_colored("=" * 50, 'blue')

        print(f"ID: {deployment['id']}")
        print(f"Статус: {deployment['phase']}")
        print(f"Причина: {deployment.get('cause', 'N/A')}")
        print(f"Создано: {self.format_timestamp(deployment['created_at'])}")
        print(f"Обновлено: {self.format_timestamp(deployment['updated_at'])}")

        if deployment.get('progress'):
            progress = deployment['progress']
            print(f"Прогресс: {progress.get('success_steps', 0)}/{progress.get('total_steps', 0)} шагов")

    def monitor(self, max_checks=10):
        """Мониторинг развертывания"""
        self.print_colored(f"🔍 НАЧИНАЮ МОНИТОРИНГ: {self.app_name}", 'yellow')
        self.print_colored(f"Интервал проверки: {self.check_interval} сек", 'yellow')
        self.print_colored(f"Максимум проверок: {max_checks}", 'yellow')
        self.print_colored("=" * 60, 'yellow')

        for check_num in range(1, max_checks + 1):
            self.print_colored(f"\n🔄 ПРОВЕРКА #{check_num} ({datetime.now().strftime('%H:%M:%S')})", 'yellow')

            # Проверка статуса приложения
            app = self.check_app_status()
            if app:
                self.display_app_info(app)

                # Проверка развертывания
                deployment = self.check_deployment_status(app['id'])
                self.display_deployment_info(deployment)

                # Проверка здоровья если приложение активно
                if app['phase'] == 'ACTIVE' and app.get('live_url'):
                    self.print_colored("\n💚 ПРОВЕРКА ЗДОРОВЬЯ", 'blue')
                    health = self.check_app_health(app['live_url'])
                    if health.get('status') == 'healthy':
                        self.print_colored("✅ Приложение здорово!", 'green')
                        print(f"Версия: {health.get('version', 'N/A')}")
                    else:
                        self.print_colored(f"❌ Проблемы со здоровьем: {health}", 'red')

                # Если приложение активно и здорово, завершить мониторинг
                if (app['phase'] == 'ACTIVE' and
                    deployment and deployment['phase'] == 'ACTIVE'):
                    self.print_colored("\n🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО!", 'green')
                    break

            else:
                self.print_colored("❌ Не удалось получить информацию о приложении", 'red')

            # Ждем перед следующей проверкой
            if check_num < max_checks:
                self.print_colored(f"\n⏳ Ожидание {self.check_interval} сек перед следующей проверкой...", 'yellow')
                time.sleep(self.check_interval)

        self.print_colored("\n🏁 МОНИТОРИНГ ЗАВЕРШЕН", 'blue')

def main():
    parser = argparse.ArgumentParser(description='Мониторинг развертывания DO App Platform')
    parser.add_argument('app_name', nargs='?', default='doteamcrn',
                       help='Имя приложения (по умолчанию: doteamcrn)')
    parser.add_argument('--interval', type=int, default=30,
                       help='Интервал проверки в секундах (по умолчанию: 30)')
    parser.add_argument('--max-checks', type=int, default=10,
                       help='Максимальное количество проверок (по умолчанию: 10)')

    args = parser.parse_args()

    monitor = DeploymentMonitor(args.app_name, args.interval)
    monitor.monitor(args.max_checks)

if __name__ == "__main__":
    main()
