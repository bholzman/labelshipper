from __future__ import absolute_import
import pytest
from models import AccountReport, AccountMeta, Account, BrokenSilence
from datetime import date


@pytest.fixture(autouse=True)
def data():
    AccountMeta.import_accounts()


@pytest.fixture(scope='module')
def csv_file():
    return 'brokensilence/2015/2015-01.csv'


def test_account_report_with_brokensilence(csv_file):
    with open(csv_file, 'r') as fh:
        bs = BrokenSilence(fh)
        bs.parse()

    account = Account('LS00024', date(2015, 1, 1), 0, 0, 0, brokensilence=[bs])
    account_report = AccountReport(account)
    html = account_report.as_html()
    assert 'Labelship' in html
    assert '23 Batt Street' in html
    assert 'Sheffield S8 0ZZ' in html
    assert 'South Yorkshire' in html
    assert 'United Kingdom' in html
