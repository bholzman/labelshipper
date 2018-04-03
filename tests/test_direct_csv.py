from __future__ import absolute_import
import pytest
from models import Direct


@pytest.fixture(scope='module')
def csv_file():
    return 'direct/2017/2017.csv'


def test_direct_csv_import(csv_file):
    with open(csv_file, 'r') as fh:
        d = Direct(fh)
        d.parse()
        assert d.tables.viewkeys() == {'direct'}

        assert d.tables['direct']['rows']
