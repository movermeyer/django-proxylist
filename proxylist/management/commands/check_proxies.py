# -*- coding: utf-8 -*-

from random import choice

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from proxylist.models import Proxy, Mirror


def check_proxies():
    mirrors = Mirror.objects.all()
    proxies = Proxy.objects.filter(next_check__lte=now())

    print '>>> %d' % proxies.count()

    for p in proxies:
        m = choice(mirrors)
        if not m.is_checking(p):
            try:
                m.check(p)
            except Exception, msg:
                print('%s - %s' % (str(p), msg))


class Command(BaseCommand):
    args = '<proxy list files>'
    help = 'Update proxy list from file(s)'

    def handle(self, *args, **options):
        check_proxies()
