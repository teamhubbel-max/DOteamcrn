"""
@file: src/reports/report_generator.py
@description: Генератор отчетов SEO анализа
@dependencies: json, datetime, typing
@created: 2024-01-01
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Генератор отчетов для результатов SEO анализа

    Создает структурированные отчеты в различных форматах:
    - HTML отчеты для веб-интерфейса
    - JSON для API
    - Текстовые сводки
    """

    def __init__(self):
        """Инициализация генератора отчетов"""
        self.templates = self._load_templates()

    def generate_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация полного отчета на основе результатов анализа

        Args:
            analysis_result (Dict[str, Any]): Результаты SEO анализа

        Returns:
            Dict[str, Any]: Сформированный отчет
        """
        try:
            logger.info('Генерируем отчет анализа')

            report = {
                'summary': self._generate_summary(analysis_result),
                'scores': self._calculate_scores(analysis_result),
                'recommendations': self._generate_recommendations(analysis_result),
                'details': analysis_result,
                'generated_at': datetime.now().isoformat()
            }

            return report

        except Exception as e:
            logger.error(f'Ошибка при генерации отчета: {str(e)}')
            return {
                'error': str(e),
                'summary': 'Ошибка генерации отчета',
                'scores': {'overall': 0},
                'recommendations': []
            }

    def _generate_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация сводки результатов анализа

        Args:
            analysis_result (Dict[str, Any]): Результаты анализа

        Returns:
            Dict[str, Any]: Сводка результатов
        """
        summary = {
            'url': analysis_result.get('url', ''),
            'status': analysis_result.get('status', 'unknown'),
            'analysis_time': round(analysis_result.get('analysis_time', 0), 2),
            'issues_count': 0,
            'warnings_count': 0,
            'passed_checks': 0,
            'failed_checks': 0
        }

        # Подсчет проблем и успешных проверок
        if 'results' in analysis_result:
            results = analysis_result['results']

            # Анализ мета-тегов
            if 'meta' in results and isinstance(results['meta'], dict):
                meta_issues = []
                for key, value in results['meta'].items():
                    if isinstance(value, dict) and 'issues' in value:
                        meta_issues.extend(value['issues'])

                summary['issues_count'] += len(meta_issues)
                if meta_issues:
                    summary['failed_checks'] += 1
                else:
                    summary['passed_checks'] += 1

            # Анализ производительности
            if 'performance' in results and isinstance(results['performance'], dict):
                if 'issues' in results['performance']:
                    perf_issues = results['performance']['issues']
                    summary['issues_count'] += len(perf_issues)
                    if perf_issues:
                        summary['failed_checks'] += 1
                    else:
                        summary['passed_checks'] += 1

            # Анализ SSL
            if 'ssl' in results and isinstance(results['ssl'], dict):
                if 'issues' in results['ssl']:
                    ssl_issues = results['ssl']['issues']
                    summary['issues_count'] += len(ssl_issues)
                    if ssl_issues:
                        summary['failed_checks'] += 1
                    else:
                        summary['passed_checks'] += 1

        return summary

    def _calculate_scores(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Расчет оценок для различных аспектов SEO

        Args:
            analysis_result (Dict[str, Any]): Результаты анализа

        Returns:
            Dict[str, Any]: Оценки по категориям
        """
        scores = {
            'meta_tags': 0,
            'performance': 0,
            'links': 0,
            'content': 0,
            'mobile': 0,
            'ssl': 0,
            'overall': 0
        }

        if 'results' not in analysis_result:
            return scores

        results = analysis_result['results']

        # Оценка мета-тегов
        if 'meta' in results and isinstance(results['meta'], dict):
            meta_score = 0
            checks = 0

            # Title оценка
            if 'title' in results['meta']:
                title = results['meta']['title']
                if title.get('optimal', False):
                    meta_score += 100
                elif title.get('length', 0) > 0:
                    meta_score += 50
                checks += 1

            # Description оценка
            if 'description' in results['meta']:
                desc = results['meta']['description']
                if desc.get('optimal', False):
                    meta_score += 100
                elif desc.get('length', 0) > 0:
                    meta_score += 50
                checks += 1

            # Viewport оценка
            if results['meta'].get('viewport', False):
                meta_score += 100
                checks += 1

            scores['meta_tags'] = meta_score // max(checks, 1)

        # Оценка производительности
        if 'performance' in results and isinstance(results['performance'], dict):
            perf = results['performance']
            if 'performance_score' in perf:
                scores['performance'] = perf['performance_score']
            elif perf.get('load_time', 0) < 2:
                scores['performance'] = 100
            elif perf.get('load_time', 0) < 5:
                scores['performance'] = 75
            elif perf.get('load_time', 0) < 10:
                scores['performance'] = 50
            else:
                scores['performance'] = 25

        # Оценка SSL
        if 'ssl' in results and isinstance(results['ssl'], dict):
            scores['ssl'] = 100 if results['ssl'].get('valid', False) else 0

        # Оценка мобильной адаптивности
        if 'mobile' in results and isinstance(results['mobile'], dict):
            scores['mobile'] = 100 if results['mobile'].get('mobile_friendly', False) else 50

        # Оценка контента
        if 'content' in results and isinstance(results['content'], dict):
            content = results['content']
            content_score = 0

            if content.get('word_count', 0) >= 300:
                content_score += 50
            if content.get('h1_count', 0) == 1:
                content_score += 30
            if content.get('img_without_alt', 0) == 0:
                content_score += 20

            scores['content'] = min(content_score, 100)

        # Общая оценка
        valid_scores = [score for score in scores.values() if score > 0]
        if valid_scores:
            scores['overall'] = sum(valid_scores) // len(valid_scores)

        return scores

    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Генерация рекомендаций по улучшению SEO

        Args:
            analysis_result (Dict[str, Any]): Результаты анализа

        Returns:
            List[Dict[str, Any]]: Список рекомендаций
        """
        recommendations = []

        if 'results' not in analysis_result:
            return recommendations

        results = analysis_result['results']

        # Рекомендации по мета-тегам
        if 'meta' in results and isinstance(results['meta'], dict):
            meta = results['meta']

            if 'title' in meta and meta['title'].get('issues'):
                recommendations.append({
                    'category': 'meta_tags',
                    'priority': 'high',
                    'title': 'Исправьте title страницы',
                    'description': '; '.join(meta['title']['issues']),
                    'solution': 'Title должен содержать 30-60 символов и включать основные ключевые слова'
                })

            if 'description' in meta and meta['description'].get('issues'):
                recommendations.append({
                    'category': 'meta_tags',
                    'priority': 'high',
                    'title': 'Исправьте meta description',
                    'description': '; '.join(meta['description']['issues']),
                    'solution': 'Description должен содержать 120-160 символов и привлекать пользователей'
                })

            if not meta.get('viewport', False):
                recommendations.append({
                    'category': 'mobile',
                    'priority': 'high',
                    'title': 'Добавьте viewport meta tag',
                    'description': 'Отсутствует viewport meta tag для мобильной адаптивности',
                    'solution': 'Добавьте <meta name="viewport" content="width=device-width, initial-scale=1">'
                })

        # Рекомендации по производительности
        if 'performance' in results and isinstance(results['performance'], dict):
            perf = results['performance']
            if perf.get('load_time', 0) > 5:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'title': 'Улучшите скорость загрузки',
                    'description': '.1f',
                    'solution': 'Оптимизируйте изображения, используйте кэширование, минимизируйте CSS/JS'
                })

        # Рекомендации по SSL
        if 'ssl' in results and isinstance(results['ssl'], dict):
            if not results['ssl'].get('valid', False):
                recommendations.append({
                    'category': 'security',
                    'priority': 'critical',
                    'title': 'Настройте SSL сертификат',
                    'description': 'SSL сертификат недействителен или отсутствует',
                    'solution': 'Получите бесплатный SSL сертификат от Let\'s Encrypt'
                })

        # Рекомендации по контенту
        if 'content' in results and isinstance(results['content'], dict):
            content = results['content']

            if content.get('h1_count', 0) != 1:
                recommendations.append({
                    'category': 'content',
                    'priority': 'medium',
                    'title': 'Исправьте структуру заголовков',
                    'description': f'Найдено {content.get("h1_count", 0)} H1 заголовков',
                    'solution': 'На странице должен быть ровно один H1 заголовок'
                })

            if content.get('word_count', 0) < 300:
                recommendations.append({
                    'category': 'content',
                    'priority': 'medium',
                    'title': 'Добавьте больше контента',
                    'description': f'Найдено всего {content.get("word_count", 0)} слов',
                    'solution': 'Добавьте качественный контент объемом не менее 300 слов'
                })

        return recommendations

    def _load_templates(self) -> Dict[str, str]:
        """
        Загрузка шаблонов отчетов

        Returns:
            Dict[str, str]: Словарь с шаблонами
        """
        # Здесь можно загрузить HTML шаблоны для отчетов
        return {
            'html_report': '',
            'summary_template': ''
        }

    def export_to_json(self, report: Dict[str, Any]) -> str:
        """
        Экспорт отчета в JSON формат

        Args:
            report (Dict[str, Any]): Отчет для экспорта

        Returns:
            str: JSON строка
        """
        return json.dumps(report, indent=2, ensure_ascii=False)

    def get_score_color(self, score: int) -> str:
        """
        Получение цвета для оценки

        Args:
            score (int): Оценка от 0 до 100

        Returns:
            str: Цвет в формате hex
        """
        if score >= 90:
            return '#28a745'  # Зеленый
        elif score >= 70:
            return '#ffc107'  # Желтый
        elif score >= 50:
            return '#fd7e14'  # Оранжевый
        else:
            return '#dc3545'  # Красный
