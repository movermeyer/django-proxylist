# -*- coding: utf-8 -*-

import os

from django.core.cache import cache

from grab import spider, Grab as GrabLib

import defaults
import models


APP_ROOT = os.path.normpath(os.path.dirname(__file__))
PC_USER_AGENT_FILE = os.path.join(APP_ROOT, 'data/pc_agents.txt')
MOBILE_USER_AGENT_FILE = os.path.join(APP_ROOT, 'data/mobile_agents.txt')


class ActiveProxiesNotFound(Exception):
    """
    Raised when active proxies not found on database
    """


def get_db_proxies(db_cache_ttl=10, grabber_cache_key='grabber_proxies_list'):
    cached = cache.get(grabber_cache_key)
    if cached:
        return cached

    proxies_list = models.Proxy.objects.values(
        'hostname', 'port', 'user', 'password'
    ).filter(errors=0, last_check__isnull=False)

    if not proxies_list.exists():
        raise ActiveProxiesNotFound

    proxies = []
    for obj in proxies_list:
        proxy = '%s:%d' % (obj['hostname'], obj['port'])
        if obj['user'] and obj['password']:
            proxy += ':%s:%s' % (obj['user'], obj['password'])
        proxies.append(proxy)
    cache.set(grabber_cache_key, proxies, db_cache_ttl)
    return proxies


def get_default_settings(mobile_devices=False):
    user_agent_file = PC_USER_AGENT_FILE
    if mobile_devices is True:
        user_agent_file = MOBILE_USER_AGENT_FILE
    return {
        'user_agent_file': user_agent_file,
        'connect_timeout': defaults.GRABBER_CONNECT_TIMEOUT,
        'timeout': defaults.GRABBER_TIMEOUT,
        'hammer_mode': True,
        'hammer_timeouts': defaults.GRABBER_HAMMER_TIMEOUTS,
        'headers': defaults.GRABBER_HEADERS
    }


class Grab(GrabLib):
    def __init__(self, *args, **kwargs):
        mobile_device = kwargs.pop('mobile_devices', False)
        db_cache_ttl = kwargs.pop('db_cache_ttl', 10)
        use_proxy = kwargs.pop('use_db_proxy', True)

        default_settings = get_default_settings(mobile_device)
        default_settings.update(kwargs)

        super(Grab, self).__init__(*args, **default_settings)

        if use_proxy is True:
            self.load_proxylist(
                source=get_db_proxies(db_cache_ttl),
                source_type='list',
                auto_init=True,
                auto_change=kwargs.get('proxy_auto_change', True)
            )


class Spider(spider.base.Spider):
    def create_grab_instance(self):
        return Grab(**self.grab_config)
