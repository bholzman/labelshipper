from __future__ import absolute_import
import pytest
from models import Account, AccountMeta, BrokenSilence, Direct
from datetime import date

@pytest.fixture(autouse=True)
def data():
    AccountMeta.import_accounts()

@pytest.fixture(scope='module')
def csv_file():
    import glob
    import random
    return random.choice(glob.glob('brokensilence/*.csv'))

@pytest.fixture(scope='module')
def direct_csv_file():
    return 'direct/2015.csv'

def test_account():
    account = Account('LS00001', date.today(), 0, 0, 0)

    with pytest.raises(AssertionError):
        account = Account('LSUNKNOWN', date.today(), 0, 0, 0)

def test_account_with_brokensilence(csv_file):
    with open(csv_file, 'r') as fh:
        bs = BrokenSilence(fh)
        bs.parse()

        account = Account('LS00024', date(2015, 1, 1), 0, 0, 0, brokensilence=[bs])
        account_data = account.report_data()
        assert account_data

def test_account_with_direct(direct_csv_file):
    with open(direct_csv_file, 'r') as fh:
        d = Direct(fh)
        d.parse()

        account = Account('LS00032', date(2015, 1, 1), 0, 0, 0, direct=[d])
        account_data = account.report_data()
        assert len(account_data) > 1
