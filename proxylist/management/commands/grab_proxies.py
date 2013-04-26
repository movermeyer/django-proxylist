# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import multiprocessing
import logging
import re

from django.core.management.base import BaseCommand
from django.conf import settings

from grab.spider.base import Spider, Task

from proxylist.defaults import PROXY_LIST_MAX_CHECK_INTERVAL as max_check
from check_proxies import check_proxies
from proxylist.models import Proxy


class GoogleSearchEngine(object):
    name = "Google"
    query = []
    page_start = 0
    page_end = 3
    page_step = 10
    start_url = "http://www.google.ru/search?q=%(q)s&hl=ru&start=%(start)d"
    xpath = '//*[@id="rso"]/li/div/h3/a'


class YandexSearchEngine(object):
    name = "Yandex"
    query = []
    page_start = 0
    page_end = 3
    page_step = 1
    start_url = "http://yandex.ru/yandsearch?p=%(start)d&text=%(q)s"
    xpath = '//h2/a'


class GrabProxies(Spider):

    initial_urls = ["http://www.google.com"]
    default_plugin = GoogleSearchEngine()
    proxy_re = r"(?:(?:[-a-z0-9]+\.)+)[a-z0-9]+:\d{2,4}"
    search_queries = [
        u"free proxy", u"free proxy list", u"бесплатные прокси",
        u"список бесплатных прокси"
    ]
    site_max_depth = 0
    timeouts = 0.1
    plugins = []
    urls = []
    configs = []

    def setup_plugins(self, *args):
        self.plugins = args

    def _load_plugins(self):
        if not self.plugins:
            self.plugins.append(self.default_plugin)
        return self.plugins

    def initial(self):
        for plugin in self._load_plugins():
            plugin.query.extend(self.search_queries)
            urls = self._pre_gen_links(plugin)
            self.urls.extend(urls)
            self.configs.append({
                "urls": urls,
                "xpath": plugin.xpath,
                "plugin": plugin.name,
            })

    def _pre_gen_links(self, plugin):
        box = []
        for query in plugin.query:
            counter = plugin.page_start
            query = query.replace(" ", "%20")
            for count in xrange(plugin.page_start, plugin.page_end):
                box.append(plugin.start_url % {'q': query, 'start': counter})
                counter += plugin.page_step
        return box

    def task_initial(self, grab, task):
        for config in self.configs:
            for url in config.get("urls"):
                yield Task('search', url=url, **config)

    def task_search(self, grab, task):
        # if grab.doc.select(task.xpath).exists():
        if grab.xpath_exists(task.xpath):
            # for element in grab.doc.select(task.xpath):
            for element in grab.xpath_list(task.xpath):
                # yield Task('find_proxy', url=element.attr('href'))
                yield Task('find_proxy', url=element.get('href'))

    def task_find_proxy(self, grab, task):
        for proxy in re.findall(self.proxy_re, grab.response.body):
            if ':' in proxy:
                proxy, port = proxy.strip().split(':')
                obj = Proxy.objects.get_or_create(hostname=proxy)[0]
                obj.port = port
                obj.next_check = datetime.now() - timedelta(seconds=max_check)
                obj.save()


class Command(BaseCommand):
    help = 'Search proxy list on internet'

    def handle(self, *args, **options):
        if settings.DEBUG:
            logging.basicConfig(level=logging.DEBUG)

        spider = GrabProxies(thread_number=(multiprocessing.cpu_count() + 1))
        spider.setup_plugins(GoogleSearchEngine(), YandexSearchEngine())
        spider.initial()
        spider.run()

        if settings.DEBUG:
            print spider.render_stats()

        check_proxies()
