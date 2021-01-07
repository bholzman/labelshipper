# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

EXPECTED_CD = {
    "LS00001": 538,
    "LS00002": 511,
    "LS00003": 0,
    "LS00004": 211,
    "LS00005": 104,
    "LS00006": 526,
    "LS00007": 439,
    "LS00009": 24,
    "LS00010": 2,
    "LS00011": 210,
    "LS00012": 3,
    "LS00013": 25,
    "LS00014": 0,
    "LS00015": 231,
    "LS00017": 64,
    "LS00018": 68,
    "LS00019": 0,
    "LS00020": 20,
    "LS00021": 20,
    "LS00022": 8,
    "LS00023": 137,
    "LS00024": 109,
    "LS00025": 311,
    "LS00026": 51,
    "LS00027": 83,
    "LS00028": 0,
    "LS00029": 30,
    "LS00030": 39,
    "LS00031": 0,
    "LS00032": 0,
    "LS00033": 36,
    "LS00034": 0,
    "LS00035": 27,
    "LS00036": 28,
    "LS00037": 280,
    "LS00038": 143,
    "LS00039": 0,
    "LS00040": 0,
    "LS00041": 106,
    "LS00042": 13,
    "LS00043": 102,
    "LS00044": 0,
}

EXPECTED_LP = {
    "LS00001": 408,
    "LS00002": 199,
    "LS00003": 0,
    "LS00004": 255,
    "LS00005": 164,
    "LS00006": 367,
    "LS00007": 0,
    "LS00009": 6,
    "LS00010": 0,
    "LS00011": 0,
    "LS00012": 0,
    "LS00013": 0,
    "LS00014": 22,
    "LS00015": 0,
    "LS00017": 0,
    "LS00018": 0,
    "LS00019": 0,
    "LS00020": 24,
    "LS00021": 0,
    "LS00022": 0,
    "LS00023": 0,
    "LS00024": 0,
    "LS00025": 0,
    "LS00026": 0,
    "LS00027": 0,
    "LS00028": 0,
    "LS00029": 0,
    "LS00030": 0,
    "LS00031": 0,
    "LS00032": 69,
    "LS00033": 0,
    "LS00034": 0,
    "LS00035": 0,
    "LS00036": 0,
    "LS00037": 0,
    "LS00038": 131,
    "LS00039": 90,
    "LS00040": 0,
    "LS00041": 303,
    "LS00042": 0,
    "LS00043": 0,
    "LS00044": 0,
}


class AccountReport(object):
    def __init__(self, account):
        self.__account = account

    def _rows(self):
        rows = ""
        for datum in self.__account.report_data():
            rows += u"""
                <tr>
                    <td>{Date}</td>
                    <td>{Transaction}</td>
                    <td>{AddDescription}</td>
                    <td>{Channel}</td>
                    <td>{Description}</td>
                    <td class="euro">{Amount:,.2f}</td>
                    <td class="int">{CD}</td>
                    <td class="int">{LP}</td>
                    <td class="int">{Digital}</td>
                    <td class="int">{StockCD}</td>
                    <td class="int">{StockLP}</td>
                </tr>
            """.format(**datum)

        return rows

    def _total(self):
        balance = 0.0
        digital = 0
        stockCD = 0
        stockLP = 0
        for datum in self.__account.report_data():
            balance += float(datum['Amount'])
            digital += int(datum['Digital'] or 0)
            stockCD += int(datum['CD'] or 0)
            stockLP += int(datum['LP'] or 0)
        # if stockCD != EXPECTED_CD[self.__account.account]:
        #     print "Stock mismatch: {} CD {} != {}".format(
        #         self.__account.account, stockCD, EXPECTED_CD[self.__account.account])
        # if stockLP != EXPECTED_LP[self.__account.account]:
        #     print "Stock mismatch: {} Vinyl {} != {}".format(
        #         self.__account.account, stockLP, EXPECTED_LP[self.__account.account])
        return """
<tfoot>
    <tr>
        <td colspan="5">TOTALS</td>
        <td class="euro">{:,.2f}</td>
        <td colspan="2"></td>
        <td class="int">{}</td>
        <td class="int">{}</td>
        <td class="int">{}</td>
    </tr>
</tfoot>""".format(balance, digital, stockCD, stockLP)

    def as_html(self):
        return (u"""
<html>
    <head>
        <meta charset="UTF-8">
        <title>{account_no} - {start_date} to {end_date}</title>
        <style type='text/css'>
            * {{
                font-size: 12px;
            }}

            body {{
                max-width: 1192px;
                width: 1192px;
            }}

            .header {{
                width: 100%;
                height: 400px;
            }}

            .title {{
                font-size: 32px;
                text-align: center;
                padding-top: 24px;
                padding-bottom: 10px;
            }}

            .logo {{
                float: left;
            }}

            .return-address {{
                float: right;
                text-align: right;
            }}

            table {{
                border-spacing: 0;
                width: 100%;
            }}

            th {{
                border-bottom: 2px solid black;
            }}

            tfoot>tr>td {{
                border-top: 2px solid black;
                font-weight: 600;
            }}

            td, th {{
                padding: 4px;
                text-align: left;
            }}

            tr>td.euro, tr>th.euro {{
                text-align: right;
            }}

            tr:first-child>td.euro::before {{
                content: "\\0020AC";
                position: relative;
                left: -12;
            }}

            td.int, th.int {{
                text-align: center;
            }}

            tr:nth-child(even) {{
                background-color: #ddd;
            }}

            @media print {{
                thead {{
                    display: table-header-group;
                }}
                tfoot {{
                    display: table-row-group;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <p class="return-address">
                 Labelship<br>
                 23 Batt Street<br>
                 Sheffield S8 0ZZ<br>
                 South Yorkshire<br>
                 United Kingdom<br>
            </p>
            <img src="http://www.labelship.com/lib/s/logo-print.png" class="logo">
            <div class="title">
                Account Statement {start_date} / {end_date}<br>
                {account_no} / {account_artist} / {account_name}
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Transaction</th>
                    <th>Add. Description</th>
                    <th>Channel</th>
                    <th>Description</th>
                    <th class="euro">Amount</th>
                    <th class="int">CD</th>
                    <th class="int">Vinyl</th>
                    <th class="int">Digital</th>
                    <th class="int">Stock CD</th>
                    <th class="int">Stock Vinyl</th>
                </tr>
            </thead>
            <tbody>
    """.format(account_no=self.__account.account,
               account_artist=self.__account.artist,
               account_name=self.__account.name,
               start_date=self.__account.start_date,
               end_date=self.__account.end_date, ) + self._rows() + """
            </tbody>
    """ + self._total() + """
    </body>
</html>""")
