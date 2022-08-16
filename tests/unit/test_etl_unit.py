import datetime
import sys

# adds a directory that should be searched
sys.path.append('/Users/mzheng/de/bitcoinDashboard/source')
from etl import get_utc_from_unix_time

def test_get_utc_from_unix_time():
    # sample unix time
    ut = 1625249025588

    # corresponding utc
    expected_dt = datetime.datetime(2021, 7, 2, 18, 3, 45, 588000)

    assert expected_dt == get_utc_from_unix_time(ut)

if __name__ == '__main__':
    test_get_utc_from_unix_time()