from __future__ import absolute_import, unicode_literals

import re
from models import AccountMeta
from datetime import date


def _parse_date(datestr):
    groups = re.match('(\d{1,2})[\-\./](\d{1,2})[\-\./](\d{4})', datestr)
    if groups:
        return date(int(groups.group(3)), int(groups.group(2)), int(groups.group(1)))
    groups = re.match('(\d{4})[\-\./](\d{1,2})[\-\./](\d{1,2})', datestr)
    if groups:
        return date(int(groups.group(1)), int(groups.group(2)), int(groups.group(3)))


class Direct(object):
    def __init__(self, fh):
        self.__fh = fh
        self.__tables = {'direct': {'rows': []}}

    @property
    def reference_number(self):
        return self.__reference_number

    @property
    def tables(self):
        return self.__tables

    def entries_for(self, account):
        entries = []
        for row in self.__tables['direct']['rows']:
            if account.account == row['account']:
                entries.append(
                    {'date': row['date'],
                     'amount': row['amount'],
                     'transaction': row['transaction'],
                     'description': row['description'],
                     'comment': row['comment'],
                     'channel': row['channel'],
                     'cds': -row['cds'] if row['cds'] else 0,
                     'lps': -row['lps'] if row['lps'] else 0, })
        return entries

    def parse(self):
        import csv
        reader = csv.reader(self.__fh)
        header = reader.next()
        assert header == [
            'DATE', 'RELEASE_ID', 'CDS', 'LPS',
            'AMOUNT', 'TRANSACTION', 'CHANNEL', 'DESCRIPTION', 'Product'
        ]
        for row in reader:
            date_, account, cds, lps, amount, transaction, channel, description, comment = row
            date_ = _parse_date(date_)
            cds = int(cds or 0)
            lps = int(lps or 0)
            amount = float(amount)
            account_meta = AccountMeta.accounts()[account]

            if not comment:
                comment = u'{} / {}'.format(account_meta.artist, account_meta.name)
                if cds > 0 and account_meta.cd_article:
                    comment += ' / {}'.format(account_meta.cd_article)
                if lps > 0 and account_meta.lp_article:
                    comment += ' / {}'.format(account_meta.lp_article)

            self.__tables['direct']['rows'].append(
                {'date': date_,
                 'account': account,
                 'amount': amount,
                 'transaction': transaction,
                 'description': description,
                 'comment': comment,
                 'channel': channel,
                 'cds': cds,
                 'lps': lps, })
