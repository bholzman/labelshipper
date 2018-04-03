# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re


class AccountMeta(object):
    def __init__(self, account, nickname, artist, name, status, digital, cd, lp, origin, bs_cd, bs_lp):
        self.__account = account
        self.__nickname = nickname
        self.__artist = artist
        self.__name = name
        self.__status = status
        self.__products = set()
        if digital:
            self.__products.add(digital)
        if cd:
            self.__products.add(cd)
        if lp:
            self.__products.add(lp)
        self.__origin = origin
        self.__articles = []
        self.__cd_article = None
        self.__lp_article = None
        if bs_cd:
            self.__articles.extend(bs_cd.split(';'))
            self.__cd_article = bs_cd
        if bs_lp:
            self.__articles.extend(bs_lp.split(';'))
            self.__lp_article = bs_lp

    @property
    def account(self):
        return self.__account

    @property
    def nickname(self):
        return self.__nickname

    @property
    def artist(self):
        return self.__artist

    @property
    def name(self):
        return self.__name

    @property
    def status(self):
        return self.__status

    @property
    def products(self):
        return self.__products

    @property
    def origin(self):
        return self.__origin

    @property
    def articles(self):
        return self.__articles if self.__articles else []

    @property
    def cd_article(self):
        return self.__cd_article

    @property
    def lp_article(self):
        return self.__lp_article

    ACCOUNTS = {}

    @classmethod
    def import_accounts(class_, source='etc/accounts.csv'):
        import csv
        with open(source, 'rb') as fh:
            reader = csv.reader(fh)
            header = reader.next()
            assert header == [
                'RELEASE_ID', 'INITIALS', 'ARTIST', 'TITLE', 'STATUS', 'DIGITAL_TYPE',
                'CD_TYPE', 'LP_TYPE', 'ORIGIN', 'BS_CD_ID', 'BS_LP_ID'
            ]
            class_.ACCOUNTS = {row[0]: AccountMeta(*[unicode(x, 'utf-8') for x in row]) for row in reader}

    @classmethod
    def accounts(class_):
        return class_.ACCOUNTS

    def has_article(self, article):
        normalized = re.sub('\*', ' ', article)
        return any(normalized == a for a in self.articles)

class Account(object):
    def __init__(self, account, start_date, start_balance, start_cd, start_lp, **kwargs):
        assert account in AccountMeta.accounts()
        self.__account = account
        self.__meta = AccountMeta.accounts()[account]
        self.__entries = [{
            'date': start_date,
            'amount': start_balance,
            'transaction': 'carry-over',
            'cds': start_cd,
            'lps': start_lp
        }]
        for bs in kwargs.get('brokensilence', []):
            self.__entries += bs.entries_for(self)
        print "For {}, found {} bs entries".format(account, len(self.__entries) - 1)
        for ds in kwargs.get('direct', []):
            self.__entries += ds.entries_for(self)

    @property
    def account(self):
        return self.__account

    @property
    def artist(self):
        return self.__meta.artist

    @property
    def name(self):
        return self.__meta.name

    @property
    def start_date(self):
        return self.__entries[0]['date']

    @property
    def end_date(self):
        return max([x['date'] for x in self.__entries])

    def has_article(self, article):
        return self.__meta.has_article(article)

    def _report_rows(self):
        stock_cds = 0
        stock_lps = 0
        for entry in sorted(self.__entries, key=lambda e: e['date']):
            stock_cds += entry.get('cds', 0)
            stock_lps += entry.get('lps', 0)
            yield {'Date': entry['date'],
                   'Transaction': entry['transaction'],
                   'AddDescription': entry.get('comment', ''),
                   'Channel': entry.get('channel', ''),
                   'Description': entry.get('description', ''),
                   'Amount': entry['amount'],
                   'CD': entry.get('cds', ''),
                   'LP': entry.get('lps', ''),
                   'Digital': entry.get('digital', ''),
                   'StockCD': stock_cds,
                   'StockLP': stock_lps, }

    def report_data(self):
        return [row for row in self._report_rows()]
