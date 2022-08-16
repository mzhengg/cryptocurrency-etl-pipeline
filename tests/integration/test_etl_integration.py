import os
import csv
import sys
import datetime
from decimal import Decimal
import psycopg2.extras as p

# location of etl.py in the container
sys.path.append('/code/source/')
from etl import warehouse_connector, run

# obtains data warehouse credentials from 'pipelinerunner' container environment
user = os.getenv('WAREHOUSE_USER', '')
password = os.getenv('WAREHOUSE_PASSWORD', '')
host = os.getenv('WAREHOUSE_HOST', '')
port = os.getenv('WAREHOUSE_PORT', '')
db = os.getenv('WAREHOUSE_DB', '')

class TestBitcoinDashboard:
    # setup() and teardown() are used to define instructions to be executed before and after each test method
    # called after test_etl_run to delete the data inside table, but not the table itself
    def teardown(self, test_etl_run):
        # connect to warehouse
        curr = warehouse_connector(user, password, host, port, db, cursor_factory=None)

        # delete all data in table, keep table
        curr.execute("TRUNCATE TABLE crypto.exchange;")

    # retrieves data from warehouse
    def retrieve_data(self):
        # connect to warehouse
        curr = warehouse_connector(user, password, host, port, db, cursor_factory=p.DictCursor)
        
        # query to select data from warehouse
        curr.execute('SELECT id, name, rank, percenttotalvolume, volumeusd, tradingpairs, socket, exchangeurl, updated_unix_millis, updated_utc FROM crypto.exchange;')
        
        # convert data to dictionary format
        table_data = [dict(r) for r in curr.fetchall()]

        return table_data

    # testing run function from etl.py
    def test_etl_run(self, mocker):
        # mock objects imitate a real object (module, class) within a test environment
        # patch allows you to mock one method of object instead of entire object
        # patch gives you control over the scope in which the object will be mocked
        # here we modify the return value of get_exchange_data to be our sample data
        mocker.patch(
            'etl.get_exchange_data',
            return_value=[r for r in csv.DictReader(open('/code/tests/integration/sample_raw_exchange_data.csv'))],
        )

        # when we call run, it will store sample_raw_exchange_data into warehouse
        run()

        # this is the data we expect to be stored in the warehouse
        expected_result = [
            {
                'id': 'binance',
                'name': 'Binance',
                'rank': 1,
                'percenttotalvolume': Decimal('25.44443'),
                'volumeusd': Decimal('12712561147.7913049212358699'),
                'tradingpairs': 650,
                'socket': True,
                'exchangeurl': 'https://www.binance.com/',
                'updated_unix_millis': 1625787943298,
                'updated_utc': datetime.datetime(2021, 7, 8, 23, 45, 43, 298000),
            },
            {
                'id': 'zg',
                'name': 'ZG.com',
                'rank': 2,
                'percenttotalvolume': Decimal('13.03445'),
                'volumeusd': Decimal('6512276458.5226475820074930'),
                'tradingpairs': 133,
                'socket': False,
                'exchangeurl': 'https://api.zg.com/',
                'updated_unix_millis': 1625787941554,
                'updated_utc': datetime.datetime(2021, 7, 8, 23, 45, 41, 554000),
            },
            {
                'id': 'huobi',
                'name': 'Huobi',
                'rank': 3,
                'percenttotalvolume': Decimal('5.93652'),
                'volumeusd': Decimal('2966009471.8337660651992927'),
                'tradingpairs': 589,
                'socket': True,
                'exchangeurl': 'https://www.hbg.com/',
                'updated_unix_millis': 1625787943276,
                'updated_utc': datetime.datetime(2021, 7, 8, 23, 45, 43, 276000),
            },
            {
                'id': 'okex',
                'name': 'Okex',
                'rank': 4,
                'percenttotalvolume': Decimal('4.99990'),
                'volumeusd': Decimal('2498051785.3601278924449889'),
                'tradingpairs': 287,
                'socket': False,
                'exchangeurl': 'https://www.okex.com/',
                'updated_unix_millis': 1625787941641,
                'updated_utc': datetime.datetime(2021, 7, 8, 23, 45, 41, 641000),
            },
        ]

        # retrieve the data stored in warehouse
        result = self.retrieve_data()

        assert expected_result == result