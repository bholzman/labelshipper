from __future__ import absolute_import, unicode_literals

import re
from models import AccountMeta
from datetime import date


def _parse_date(datestr):
    groups = re.match('(\d{2})\.(\d{2})\.(\d{4})', datestr)
    if groups:
        return date(int(groups.group(3)), int(groups.group(2)), int(groups.group(1)))


class BrokenSilence(object):
    def __init__(self, fh):
        self.__fh = fh
        self.__tables = {}
        self.__reference_number = None
        self.__curtbl = None

    @property
    def reference_number(self):
        return self.__reference_number

    @property
    def tables(self):
        return self.__tables

    def all_articles(self):
        all_articles = set([])
        if 'national' in self.__tables:
            for row in self.__tables['national']['rows']:
                all_articles.add(row['article no'])
        if 'international' in self.__tables:
            for row in self.__tables['international']['rows']:
                all_articles.add(row['article no.'])
        if 'downloads' in self.__tables:
            for row in self.__tables['downloads']['rows']:
                all_articles.add(row['article no.'])
        if 'digital' in self.__tables:
            for row in self.__tables['digital']['rows']:
                all_articles.add(row['article no.'])

        return all_articles
    
    def entries_for(self, account):
        account_meta = AccountMeta.accounts()[account.account]
        entries = []
        def comment(article_no):
            comment = '{} / {}'.format(account_meta.artist, account_meta.name)
            if article_no.startswith('CD') and account_meta.cd_article:
                comment += ' / {}'.format(account_meta.cd_article)
            if not article_no.startswith('CD') and account_meta.lp_article:
                comment += ' / {}'.format(account_meta.lp_article)
            return comment

        if 'national' in self.__tables:
            report_date = _parse_date(self.__tables['national']['report_date'])
            for row in self.__tables['national']['rows']:
                is_cd = row['article no'].startswith('CD')
                if account.has_article(row['article no']):
                    sales_count = int(row['domestic qty/dealer/net(aver.)'][0])
                    if sales_count:
                        amount = float(row['amount domestic'])
                        entries.append(
                            {'date': report_date,
                             'amount': amount,
                             'transaction': 'sale' if amount >= 0 else 'return',
                             'channel': 'Brokensilence',
                             'comment': comment(row['article no']),
                             'cds': -sales_count if is_cd else 0,
                             'lps': 0 if is_cd else -sales_count, })

                    return_key = 'returns domestic qty/dealer/net(aver.)'
                    if return_key not in row:
                        return_key = 'returns domestic qty/dealer/domestic net(aver.)'
                    return_count = int(row[return_key][0])
                    if return_count:
                        entries.append(
                            {'date': report_date,
                             'amount': float(row['amount returns domestic']),
                             'transaction': 'return',
                             'channel': 'Brokensilence',
                             'comment': comment(row['article no']),
                             'cds': return_count if is_cd else 0,
                             'lps': 0 if is_cd else return_count, })
                    stock_arrivals, stock_dispatches = map(int, row['arrivals dispatch'])
                    if stock_arrivals > 0:
                        entries.append(
                            {'date': report_date,
                             'amount': 0.0,
                             'transaction': 'stock in',
                             'channel': 'Brokensilence',
                             'comment': comment(row['article no']), 
                             'cds': stock_arrivals if is_cd else 0,
                             'lps': 0 if is_cd else stock_arrivals, })
                    if stock_dispatches > 0:
                        entries.append(
                            {'date': report_date,
                             'amount': 0.0,
                             'transaction': 'stock out',
                             'channel': 'Brokensilence',
                             'comment': comment(row['article no']), 
                             'cds': -stock_dispatches if is_cd else 0,
                             'lps': 0 if is_cd else -stock_dispatches, })

        if 'international' in self.__tables:
            report_date = _parse_date(self.__tables['international']['report_date'])
            for row in self.__tables['international']['rows']:
                if account.has_article(row['article no.']):
                    sales_count = int(row['export sales/prices'][0])
                    if sales_count:
                        amount = float(row['amount export'])
                        entries.append(
                            {'date':  report_date,
                             'amount': amount,
                             'transaction': 'sale' if amount >= 0 else 'return',
                             'channel': 'Brokensilence',
                             'comment': comment(row['article no.']),
                             'cds': -sales_count if row['article no.'].startswith('CD') else 0,
                             'lps': 0 if row['article no.'].startswith('CD') else -sales_count, })
                    return_count = int(row['returns export qty/dealer/net(aver.)'][0])
                    if return_count:
                        entries.append(
                            {'date': report_date,
                             'amount': float(row['amount returns exp.']),
                             'transaction': 'return',
                             'channel': 'Brokensilence',
                             'comment': comment(row['article no.']),
                             'cds': return_count if row['article no.'].startswith('CD') else 0,
                             'lps': 0 if row['article no.'].startswith('CD') else return_count, })

        if 'downloads' in self.__tables:
            report_date = _parse_date(self.__tables['downloads']['report_date'])
            for row in self.__tables['downloads']['rows']:
                if account.has_article(row['article no.']):
                    entries.append(
                        {'date': report_date,
                         'amount': float(row['total amount']),
                         'transaction': 'download/stream',
                         'comment': (u'/'.join(row['track'])
                                     if isinstance(row['track'], (tuple, list))
                                     else row['track']),
                         'channel': '/'.join(row['shop']) if isinstance(row['shop'], (tuple, list)) else row['shop'],
                         'digital': int(row['domestic'][0])})

        if 'digital' in self.__tables:
            report_date = _parse_date(self.__tables['digital']['report_date'])
            for row in self.__tables['digital']['rows']:
                if account.has_article(row['article no.']):
                    entries.append(
                        {'date': report_date,
                         'amount': float(row['total amount']),
                         'transaction': 'download/stream',
                         'comment': (u'/'.join(row['track'])
                                     if isinstance(row['track'], (tuple, list))
                                     else row['track']),
                         'channel': '/'.join(row['shop']) if isinstance(row['shop'], (tuple, list)) else row['shop'],
                         'digital': int(row['qty'][0])})

        return entries

    def _cells_by_column(self, cells, columns):
        def _clean(elem):
            return re.sub('(\d+),(\d+)', '\\1.\\2', elem)

        def _expand(cell):
            elems = cell.split('/')
            if len(elems) == 1:
                return _clean(elems[0])
            else:
                return map(lambda x: _clean(x.strip()), elems)
        return {c: _expand(cells[i]) for i, c in enumerate(self.__curtbl[columns])}

    def parse(self):
        def _newtbl():
            return {
                'report_date': report_date,
                'sales_start': sales_start,
                'sales_end': sales_end,
                'columns': [],
                'rows': [],
                'total_columns': [],
                'totals': {}
            }

        for raw in self.__fh:
            row = unicode(raw, 'iso-8859-1').strip()
            match = re.match(
                '^statement (\w+) reference no: (\d+), date: (\d\d\.\d\d\.\d{4}), '
                'salesperiode: (\d\d\.\d\d\.\d{4})?-(\d\d\.\d\d\.\d{4})?$', row)
            if match:
                statement_type, ref_no, report_date, sales_start, sales_end = match.groups()
                self.__tables[statement_type] = _newtbl()
                self.__curtbl = self.__tables[statement_type]
                if self.__reference_number:
                    if ref_no != self.__reference_number:
                        raise Exception(
                            "Multiple Reference Numbers Found: {} != {}".format(ref_no, self.__reference_number))
                else:
                    self.__reference_number = ref_no
            elif re.match('^summary physical sales$', row):
                statement_type = 'physical_summary'
                self.__tables[statement_type] = _newtbl()
                self.__curtbl = self.__tables[statement_type]
            elif self.__curtbl:
                if row:
                    cells = row.split(';')
                    if cells[0].startswith('total'):
                        self.__curtbl['total_columns'] = cells
                    elif self.__curtbl['total_columns']:
                        if len(cells) != len(self.__curtbl['total_columns']):
                            raise Exception(
                                "Inconsistent Row Found: {} != {}".format(cells, self.__curtbl['total_columns']))
                        else:
                            self.__curtbl['totals'] = self._cells_by_column(cells, 'total_columns')
                    elif self.__curtbl['columns']:
                        if len(cells) != len(self.__curtbl['columns']):
                            raise Exception("Inconsistent Row Found: {} != {}".format(cells, self.__curtbl['columns']))
                        else:
                            self.__curtbl['rows'].append(self._cells_by_column(cells, 'columns'))
                    else:
                        self.__curtbl['columns'] = cells[:]
