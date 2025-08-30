"""
@file: src/app/routes.py
@description: Маршруты веб-приложения SEO Audit Tool
@dependencies: Flask, src.seo_analyzer, src.reports
@created: 2024-01-01
"""

import logging
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from ..seo_analyzer import SEOAnalyzer
from ..reports import ReportGenerator

# Создание blueprint
main_bp = Blueprint('main', __name__)

# Инициализация анализатора и генератора отчетов
seo_analyzer = SEOAnalyzer()
report_generator = ReportGenerator()

logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """
    Главная страница приложения

    Returns:
        str: HTML шаблон главной страницы
    """
    return render_template('index.html')

@main_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Анализ SEO параметров сайта

    Returns:
        JSON: Результаты анализа или перенаправление
    """
    try:
        url = request.form.get('url', '').strip()

        if not url:
            flash('Пожалуйста, введите URL для анализа', 'error')
            return redirect(url_for('main.index'))

        # Валидация URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        logger.info(f'Начинаем анализ сайта: {url}')

        # Выполнение SEO анализа
        analysis_result = seo_analyzer.analyze_site(url)

        # Генерация отчета
        report = report_generator.generate_report(analysis_result)

        return render_template('results.html',
                             url=url,
                             analysis=analysis_result,
                             report=report)

    except Exception as e:
        logger.error(f'Ошибка при анализе сайта: {str(e)}')
        flash(f'Произошла ошибка при анализе: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    API endpoint для анализа SEO

    Returns:
        JSON: Результаты анализа в формате JSON
    """
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({
                'error': 'URL обязателен для анализа'
            }), 400

        url = data['url'].strip()

        # Валидация URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        logger.info(f'API анализ сайта: {url}')

        # Выполнение анализа
        result = seo_analyzer.analyze_site(url)

        return jsonify({
            'success': True,
            'url': url,
            'analysis': result,
            'timestamp': result.get('timestamp')
        })

    except Exception as e:
        logger.error(f'API ошибка: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/health')
def health():
    """
    Проверка здоровья приложения

    Returns:
        JSON: Статус приложения
    """
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': seo_analyzer.get_timestamp()
    })

@main_bp.route('/about')
def about():
    """
    Страница "О программе"

    Returns:
        str: HTML шаблон страницы about
    """
    return render_template('about.html')

@main_bp.errorhandler(404)
def page_not_found(e):
    """Обработчик ошибки 404"""
    return render_template('404.html'), 404

@main_bp.errorhandler(500)
def internal_error(e):
    """Обработчик ошибки 500"""
    logger.error(f'Внутренняя ошибка сервера: {str(e)}')
    return render_template('500.html'), 500
