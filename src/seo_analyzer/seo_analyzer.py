"""
@file: src/seo_analyzer/seo_analyzer.py
@description: Основной класс SEO анализатора
@dependencies: requests, datetime, logging, meta_analyzer, speed_analyzer, link_analyzer
@created: 2024-01-01
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    """
    Основной класс для комплексного SEO анализа сайта

    Выполняет анализ различных аспектов оптимизации:
    - Мета-теги (title, description, keywords)
    - Скорость загрузки
    - Структура ссылок
    - Мобильная адаптивность
    - Контент анализ
    """

    def __init__(self, timeout: int = 30, max_redirects: int = 5):
        """
        Инициализация SEO анализатора

        Args:
            timeout (int): Таймаут для HTTP запросов в секундах
            max_redirects (int): Максимальное количество перенаправлений
        """
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session = requests.Session()
        self.session.max_redirects = max_redirects

        # Настройка заголовков
        self.session.headers.update({
            'User-Agent': 'SEO-Audit-Tool/1.0 (https://seo-audit-tool.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def analyze_site(self, url: str) -> Dict[str, Any]:
        """
        Выполнение комплексного SEO анализа сайта

        Args:
            url (str): URL сайта для анализа

        Returns:
            Dict[str, Any]: Результаты анализа
        """
        logger.info(f'Начинаем комплексный SEO анализ сайта: {url}')

        start_time = time.time()
        result = {
            'url': url,
            'timestamp': self.get_timestamp(),
            'analysis_time': 0,
            'status': 'analyzing',
            'errors': [],
            'results': {}
        }

        try:
            # Проверка доступности сайта
            response = self._check_site_availability(url)
            if not response:
                result['status'] = 'error'
                result['errors'].append('Сайт недоступен')
                return result

            result['results']['availability'] = {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'final_url': response.url
            }

            # Анализ мета-тегов
            result['results']['meta'] = self._analyze_meta_tags(response)

            # Анализ структуры ссылок
            result['results']['links'] = self._analyze_links(response, url)

            # Анализ контента
            result['results']['content'] = self._analyze_content(response)

            # Анализ скорости загрузки
            result['results']['performance'] = self._analyze_performance(url)

            # Проверка мобильной адаптивности
            result['results']['mobile'] = self._analyze_mobile_friendly(url)

            # Проверка SSL сертификата
            result['results']['ssl'] = self._check_ssl_certificate(url)

            result['status'] = 'completed'

        except Exception as e:
            logger.error(f'Ошибка при анализе сайта {url}: {str(e)}')
            result['status'] = 'error'
            result['errors'].append(str(e))

        finally:
            result['analysis_time'] = time.time() - start_time
            logger.info(f'Анализ завершен за {result["analysis_time"]:.2f} сек')
        return result

    def _check_site_availability(self, url: str) -> Optional[requests.Response]:
        """
        Проверка доступности сайта

        Args:
            url (str): URL для проверки

        Returns:
            Optional[requests.Response]: HTTP ответ или None при ошибке
        """
        try:
            logger.debug(f'Проверяем доступность: {url}')
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f'Ошибка при проверке доступности {url}: {str(e)}')
            return None

    def _analyze_meta_tags(self, response: requests.Response) -> Dict[str, Any]:
        """
        Анализ мета-тегов страницы

        Args:
            response (requests.Response): HTTP ответ

        Returns:
            Dict[str, Any]: Результаты анализа мета-тегов
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.content, 'html.parser')

            result = {
                'title': {
                    'content': '',
                    'length': 0,
                    'optimal': False,
                    'issues': []
                },
                'description': {
                    'content': '',
                    'length': 0,
                    'optimal': False,
                    'issues': []
                },
                'keywords': {
                    'content': '',
                    'count': 0,
                    'issues': []
                },
                'viewport': False,
                'robots': False
            }

            # Анализ title
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text().strip()
                result['title']['content'] = title_text
                result['title']['length'] = len(title_text)

                if len(title_text) < 30:
                    result['title']['issues'].append('Title слишком короткий (< 30 символов)')
                elif len(title_text) > 60:
                    result['title']['issues'].append('Title слишком длинный (> 60 символов)')
                else:
                    result['title']['optimal'] = True

            # Анализ description
            desc_meta = soup.find('meta', attrs={'name': 'description'})
            if desc_meta and desc_meta.get('content'):
                desc_text = desc_meta['content'].strip()
                result['description']['content'] = desc_text
                result['description']['length'] = len(desc_text)

                if len(desc_text) < 120:
                    result['description']['issues'].append('Description слишком короткий (< 120 символов)')
                elif len(desc_text) > 160:
                    result['description']['issues'].append('Description слишком длинный (> 160 символов)')
                else:
                    result['description']['optimal'] = True

            # Анализ keywords
            keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_meta and keywords_meta.get('content'):
                keywords = keywords_meta['content'].strip()
                result['keywords']['content'] = keywords
                result['keywords']['count'] = len([k.strip() for k in keywords.split(',') if k.strip()])

                if result['keywords']['count'] > 10:
                    result['keywords']['issues'].append('Слишком много ключевых слов (> 10)')

            # Проверка viewport
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            result['viewport'] = viewport_meta is not None

            # Проверка robots
            robots_meta = soup.find('meta', attrs={'name': 'robots'})
            result['robots'] = robots_meta is not None

            return result

        except Exception as e:
            logger.error(f'Ошибка при анализе мета-тегов: {str(e)}')
            return {'error': str(e)}

    def _analyze_links(self, response: requests.Response, base_url: str) -> Dict[str, Any]:
        """
        Анализ структуры ссылок на странице

        Args:
            response (requests.Response): HTTP ответ
            base_url (str): Базовый URL сайта

        Returns:
            Dict[str, Any]: Результаты анализа ссылок
        """
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urlparse

            soup = BeautifulSoup(response.content, 'html.parser')

            result = {
                'internal_links': 0,
                'external_links': 0,
                'broken_links': 0,
                'links_without_alt': 0,
                'total_links': 0
            }

            base_domain = urlparse(base_url).netloc

            for link in soup.find_all('a', href=True):
                result['total_links'] += 1
                href = link['href']

                # Проверка изображений без alt
                if link.find('img') and not link.find('img').get('alt'):
                    result['links_without_alt'] += 1

                try:
                    # Преобразование относительных ссылок в абсолютные
                    absolute_url = urljoin(base_url, href)
                    link_domain = urlparse(absolute_url).netloc

                    if link_domain == base_domain:
                        result['internal_links'] += 1
                    else:
                        result['external_links'] += 1

                except Exception:
                    result['broken_links'] += 1

            return result

        except Exception as e:
            logger.error(f'Ошибка при анализе ссылок: {str(e)}')
            return {'error': str(e)}

    def _analyze_content(self, response: requests.Response) -> Dict[str, Any]:
        """
        Анализ контента страницы

        Args:
            response (requests.Response): HTTP ответ

        Returns:
            Dict[str, Any]: Результаты анализа контента
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.content, 'html.parser')

            # Извлечение текстового контента
            for script in soup(["script", "style"]):
                script.decompose()

            text_content = soup.get_text(separator=' ', strip=True)

            result = {
                'word_count': len(text_content.split()),
                'char_count': len(text_content),
                'h1_count': len(soup.find_all('h1')),
                'h2_count': len(soup.find_all('h2')),
                'h3_count': len(soup.find_all('h3')),
                'img_count': len(soup.find_all('img')),
                'img_without_alt': 0,
                'issues': []
            }

            # Проверка изображений без alt
            for img in soup.find_all('img'):
                if not img.get('alt'):
                    result['img_without_alt'] += 1

            # Проверка структуры заголовков
            if result['h1_count'] == 0:
                result['issues'].append('Отсутствует H1 заголовок')
            elif result['h1_count'] > 1:
                result['issues'].append('Несколько H1 заголовков на странице')

            if result['word_count'] < 300:
                result['issues'].append('Недостаточно контента на странице (< 300 слов)')

            return result

        except Exception as e:
            logger.error(f'Ошибка при анализе контента: {str(e)}')
            return {'error': str(e)}

    def _analyze_performance(self, url: str) -> Dict[str, Any]:
        """
        Анализ производительности сайта

        Args:
            url (str): URL для анализа

        Returns:
            Dict[str, Any]: Результаты анализа производительности
        """
        try:
            import time

            start_time = time.time()
            response = self.session.get(url, timeout=self.timeout)
            load_time = time.time() - start_time

            result = {
                'load_time': round(load_time, 2),
                'response_size': len(response.content),
                'status_code': response.status_code,
                'performance_score': 0,
                'issues': []
            }

            # Оценка производительности
            if load_time < 2:
                result['performance_score'] = 100
            elif load_time < 5:
                result['performance_score'] = 75
            elif load_time < 10:
                result['performance_score'] = 50
            else:
                result['performance_score'] = 25
                result['issues'].append('Слишком долгое время загрузки (> 10 сек)')

            if response.status_code != 200:
                result['issues'].append(f'Некорректный статус код: {response.status_code}')

            return result

        except Exception as e:
            logger.error(f'Ошибка при анализе производительности: {str(e)}')
            return {'error': str(e)}

    def _analyze_mobile_friendly(self, url: str) -> Dict[str, Any]:
        """
        Анализ мобильной адаптивности

        Args:
            url (str): URL для анализа

        Returns:
            Dict[str, Any]: Результаты анализа мобильной адаптивности
        """
        try:
            # Базовая проверка viewport meta tag
            response = self.session.get(url, timeout=self.timeout)
            content = response.text.lower()

            result = {
                'viewport_meta': 'viewport' in content,
                'mobile_friendly': False,
                'issues': []
            }

            if not result['viewport_meta']:
                result['issues'].append('Отсутствует viewport meta tag')

            # Простая проверка на наличие responsive элементов
            if 'media=' in content or '@media' in content:
                result['mobile_friendly'] = True
            else:
                result['issues'].append('Возможны проблемы с мобильной адаптивностью')

            return result

        except Exception as e:
            logger.error(f'Ошибка при анализе мобильной адаптивности: {str(e)}')
            return {'error': str(e)}

    def _check_ssl_certificate(self, url: str) -> Dict[str, Any]:
        """
        Проверка SSL сертификата

        Args:
            url (str): URL для проверки

        Returns:
            Dict[str, Any]: Результаты проверки SSL
        """
        try:
            import ssl
            from urllib.parse import urlparse

            parsed_url = urlparse(url)
            hostname = parsed_url.hostname

            if not hostname:
                return {'error': 'Некорректный URL'}

            context = ssl.create_default_context()
            with context.wrap_socket(ssl.socket(), server_hostname=hostname) as sock:
                sock.connect((hostname, 443))
                cert = sock.getpeercert()

            result = {
                'valid': True,
                'issuer': dict(cert.get('issuer', [])),
                'subject': dict(cert.get('subject', [])),
                'expires': cert.get('notAfter'),
                'issues': []
            }

            return result

        except Exception as e:
            logger.error(f'Ошибка при проверке SSL: {str(e)}')
            return {
                'valid': False,
                'error': str(e),
                'issues': ['SSL сертификат недействителен или отсутствует']
            }

    @staticmethod
    def get_timestamp() -> str:
        """Получение текущего timestamp в формате ISO"""
        return datetime.now().isoformat()
