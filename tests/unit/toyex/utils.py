import datetime
from celery_uncovered.toyex.utils import strf_date

def test_strf_date():
    ref_date = datetime.datetime(year=2017, month=06, day=01)
    assert strf_date('day', ref_date=ref_date).startswith('2017-05-31')
    assert strf_date('week', ref_date=ref_date).startswith('2017-05-25')
    assert strf_date('month', ref_date=ref_date).startswith('2017-05-02')

    assert strf_date(ref_date, ref_date=ref_date).startswith('2017-06-01')


