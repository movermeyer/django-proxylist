# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from proxylist.models import Proxy


def clean_proxies():
    Proxy.objects.filter(errors__gt=0).delete()


class Command(BaseCommand):
    help = 'Remove broken proxies.'

    def handle(self, *args, **options):
        clean_proxies()
