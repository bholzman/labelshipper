from __future__ import absolute_import
import pytest
from models import BrokenSilence


ERROR_THRESHOLD = 1.0000000001e-2


@pytest.fixture(scope='module')
def csv_file():
    return 'brokensilence/2016/2016-01.csv'


def test_brokensilence_csv_import(csv_file):
    with open(csv_file, 'r') as fh:
        bs = BrokenSilence(fh)
        bs.parse()
        # assert bs.reference_number == '920880'
        assert (bs.tables.viewkeys() == {'national', 'international', 'downloads'} or
                bs.tables.viewkeys() == {'national', 'international', 'downloads', 'physical_summary'})

        for table_type, table in bs.tables.iteritems():
            assert table['report_date'] == bs.tables['national']['report_date']
            assert all(row.viewkeys() == set(table['columns']) for row in table['rows'])
            if table_type != 'physical_summary':
                assert table['total_columns']
                assert table['totals']
                assert table['totals'].viewkeys() == set(table['total_columns'])

        # sanity check
        assert bs.tables['national']['columns'][0] == 'article no'


def test_brokensilence_validate_national_totals(csv_file):
    with open(csv_file, 'r') as fh:
        bs = BrokenSilence(fh)
        bs.parse()

        national = bs.tables['national']

        # cross-check sales count
        national_sales_total = sum(int(row['domestic qty/dealer/net(aver.)'][0]) for row in national['rows'])
        assert national_sales_total == int(national['totals']['total sales domestic'])

        # cross-check sales amount
        national_amount_total = sum(float(row['amount domestic']) for row in national['rows'])
        assert abs(national_amount_total - float(national['totals']['total amount domestic'])) < ERROR_THRESHOLD

        # cross-check return count
        national_returns_total = sum(int(row['returns domestic qty/dealer/net(aver.)'][0]) for row in national['rows'])
        assert national_returns_total == int(national['totals']['total returns domestic'])

        # cross-check return amount
        national_return_amount_total = sum(float(row['amount returns domestic']) for row in national['rows'])
        assert abs(national_return_amount_total - float(national['totals']['ret amount domestic'])) < ERROR_THRESHOLD

        # check that national total is sum of amount domestic and ret amount domestic
        assert abs(float(national['totals']['total value']) - (
            float(national['totals']['total amount domestic']) +
            float(national['totals']['ret amount domestic']))) < ERROR_THRESHOLD


def test_brokensilence_validate_international_totals(csv_file):
    with open(csv_file, 'r') as fh:
        bs = BrokenSilence(fh)
        bs.parse()

        # do not have an example of this table so can only cross-check the totals against themselves
        table = bs.tables['international']
        assert abs(float(table['totals']['total value']) - (
            float(table['totals']['total amount export']) +
            float(table['totals']['total amount returns exp.']))) < ERROR_THRESHOLD


def test_brokensilence_validate_downloads_totals(csv_file):
    with open(csv_file, 'r') as fh:
        bs = BrokenSilence(fh)
        bs.parse()

        table = bs.tables['downloads']

        # cross-check count
        download_count = sum(int(row['domestic'][0]) for row in table['rows'])
        assert download_count == int(table['totals']['total sales'])

        # cross-check amount
        download_amount = sum(float(row['total amount']) for row in table['rows'])
        assert abs(float(table['totals']['total amount']) - download_amount) < 1
