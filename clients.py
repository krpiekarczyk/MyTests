import re
import bs4

import requests


class _CachedHttpProvider:

    def __init__(self, http_provider):
        self.http_provider = http_provider
        self.cache = {}

    def __getattr__(self, item):
        return getattr(self.http_provider, item)

    def get(self, url):
        if url not in self.cache:
            self.cache[url] = self.http_provider.get(url)
        return self.cache[url]


cached_http_provider = _CachedHttpProvider(requests)


class BaseClient:

    def __init__(self, http_provider=cached_http_provider):
        self.http_provider = http_provider


class PlejadaSingleGalleryClient(BaseClient):

    def get_all_page_numbers(self, start_url):
        parsers = self._plejada_gallery_iter(start_url, self.http_provider)
        return [parser.get_page_nr() for parser in parsers]

    def get_page_count(self, url):
        response = self.http_provider.get(url)
        parser = _PlejadaGalleryHtmlParser(response.text)
        return parser.get_pages_count()

    def _plejada_gallery_iter(self, start_url, http_provider):
        url = start_url
        while True:
            response = http_provider.get(url)
            parser = _PlejadaGalleryHtmlParser(html=response.text)
            if parser.is_end_page():
                break
            else:
                yield parser
                url = parser.get_url_of_next_page()


class PlejadaMainGalleryClient(BaseClient):
    url = 'http://plejada.onet.pl/'

    def __init__(self, driver):
        super(BaseClient).__init__()
        self.driver = driver

    def visit_page(self, url=None):
        self.driver.get(url or self.url)

    def count_gallery_images(self):
        parser = _PlejadaMainGalleryHtmlParser(self.driver.page_source)
        return parser.count_images()

    def scroll_down(self, times=10, seconds=1):
        self._scroll_down()
        for _ in range(times-1):
            self.wait(seconds)
            self._scroll_down()

    def wait(self, seconds):
        self.driver.implicitly_wait(seconds * 1000)

    def _scroll_down(self):
        script = 'window.scrollTo(0, document.body.scrollHeight);'
        self.driver.execute_script(script)


class _PlejadaGalleryHtmlParser:
    page_nr_re = re.compile(r'\(slajd.(\d+).+\)')
    page_count_re = re.compile(r'\(slajd.(\d+).+(\d+)\)')
    base_url = 'http://plejada.onet.pl'
    end_page_text = 'Mog&#261; Ci&#281; r&#243;wnie&#380; zainteresowa&#263; '

    def __init__(self, html):
        self.html = html
        self.soup = bs4.BeautifulSoup(html)

    def is_end_page(self):
        return self.end_page_text in self.html

    def get_page_nr(self):
        element = self.soup.find('div', id='mainMediaTitle')
        digits = _select_text(element.string, self.page_nr_re, group_nr=1)
        return int(digits)

    def get_pages_count(self):
        element = self.soup.find('div', id='mainMediaTitle')
        digits = _select_text(element.string, self.page_count_re, group_nr=2)
        return int(digits)

    def get_url_of_next_page(self):
        element = self.soup.find('a', alt='Następny')
        return self.base_url + element.get('href')


class _PlejadaMainGalleryHtmlParser:

    def __init__(self, html):
        self.html = html
        self.soup = bs4.BeautifulSoup(html)

    def count_images(self):
        small_images = self.soup.find_all('img', class_='smallImg')
        big_images = self.soup.find_all('img', class_='bigImg')
        return len(small_images) + len(big_images)


def _select_text(text, pattern, group_nr=0):
    return pattern.search(text).group(group_nr)
