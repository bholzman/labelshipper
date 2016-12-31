from __future__ import absolute_import, unicode_literals

import re
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

    def entries_for(self, account):
        entries = []
        if 'national' in self.__tables:
            report_date = _parse_date(self.__tables['national']['report_date'])
            for row in self.__tables['national']['rows']:
                if account.has_article(row['article no']):
                    sales_count = int(row['domestic qty/dealer/net(aver.)'][0])
                    if sales_count:
                        entries.append(
                            {'date': report_date,
                             'amount': float(row['amount domestic']),
                             'transaction': 'sale',
                             'channel': 'Brokensilence',
                             'cds': -sales_count if row['article no'].startswith('CD') else 0,
                             'lps': 0 if row['article no'].startswith('CD') else -sales_count, })
                    return_count = int(row['returns domestic qty/dealer/net(aver.)'][0])
                    if return_count:
                        entries.append(
                            {'date': report_date,
                             'amount': float(row['amount returns domestic']),
                             'transaction': 'return',
                             'channel': 'Brokensilence',
                             'cds': return_count if row['article no'].startswith('CD') else 0,
                             'lps': 0 if row['article no'].startswith('CD') else return_count, })

        if 'international' in self.__tables:
            report_date = _parse_date(self.__tables['international']['report_date'])
            for row in self.__tables['international']['rows']:
                if account.has_article(row['article no.']):
                    sales_count = int(row['export sales/prices'][0])
                    if sales_count:
                        entries.append(
                            {'date':  report_date,
                             'amount': float(row['amount export']),
                             'transaction': 'sale',
                             'channel': 'Brokensilence',
                             'cds': -sales_count if row['article no.'].startswith('CD') else 0,
                             'lps': 0 if row['article no.'].startswith('CD') else -sales_count, })
                    return_count = int(row['returns export qty/dealer/net(aver.)'][0])
                    if return_count:
                        entries.append(
                            {'date': report_date,
                             'amount': float(row['amount returns exp.']),
                             'transaction': 'return',
                             'channel': 'Brokensilence',
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
                         'channel': row['shop'],
                         'digital': int(row['domestic'][0])})

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
