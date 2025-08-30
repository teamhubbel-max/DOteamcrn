"""
@file: src/app/__init__.py
@description: Инициализация Flask приложения SEO Audit Tool
@dependencies: Flask, os, logging
@created: 2024-01-01
"""

import os
import logging
from flask import Flask
from logging.config import dictConfig

def create_app(config_name=None):
    """
    Фабрика приложения Flask для SEO Audit Tool

    Args:
        config_name (str): Имя конфигурации (development/production)

    Returns:
        Flask: Настроенное Flask приложение
    """
    # Настройка путей для шаблонов и статических файлов
    import os
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')

    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)

    # Настройка конфигурации
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    configure_app(app, config_name)

    # Настройка логирования
    configure_logging(app)

    # Регистрация blueprints
    register_blueprints(app)

    # Инициализация расширений
    initialize_extensions(app)

    return app

def configure_app(app, config_name):
    """Настройка конфигурации приложения"""

    # Базовая конфигурация
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        DEBUG=config_name == 'development',
        TESTING=config_name == 'testing',

        # Настройки SEO анализа
        MAX_ANALYSIS_TIME=int(os.getenv('MAX_ANALYSIS_TIME', 30)),  # секунды
        MAX_URLS_PER_ANALYSIS=int(os.getenv('MAX_URLS_PER_ANALYSIS', 10)),
        USER_AGENT='SEO-Audit-Tool/1.0',

        # Настройки для DigitalOcean
        DO_APP=True if os.getenv('DO_APP') else False,
    )

    # Конфигурация для разработки
    if config_name == 'development':
        app.config.update(
            DEBUG=True,
            TEMPLATES_AUTO_RELOAD=True,
        )

    # Конфигурация для продакшена
    elif config_name == 'production':
        app.config.update(
            DEBUG=False,
            TESTING=False,
        )

def configure_logging(app):
    """Настройка системы логирования"""

    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    })

    app.logger.info('SEO Audit Tool запущен')

def register_blueprints(app):
    """Регистрация blueprints (маршрутов)"""

    from .routes import main_bp
    app.register_blueprint(main_bp)

    app.logger.info('Blueprints зарегистрированы')

def initialize_extensions(app):
    """Инициализация расширений Flask"""

    # Здесь можно инициализировать дополнительные расширения
    # Например: database, cache, etc.

    app.logger.info('Расширения инициализированы')

# Создание экземпляра приложения для Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
