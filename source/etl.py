import os
import datetime
import psycopg2
import psycopg2.extras as p
import requests

# obtains data warehouse credentials from 'pipelinerunner' container environment
user = os.getenv('WAREHOUSE_USER', '')
password = os.getenv('WAREHOUSE_PASSWORD', '')
host = os.getenv('WAREHOUSE_HOST', '')
port = os.getenv('WAREHOUSE_PORT', '')
db = os.getenv('WAREHOUSE_DB', '')

# convert unix time (ms) into UTC
def get_utc_from_unix_time(unix_ts, second=1000):
    # first convert unix to seconds, then use func to get utc
    return (datetime.datetime.utcfromtimestamp(int(unix_ts)/second) if unix_ts else None)

# pull data from CoinCap API
def get_exchange_data():
    # link to API
    url = 'https://api.coincap.io/v2/exchanges'

    try:
        # sends a GET request to API
        r = requests.get(url)

    except requests.ConnectionError as ce:
        print(f"There was an error with the request, {ce}")
        return

    # retrieve a list of data from 'data' (in json format)
    # each list entry is a dictionary object
    return r.json().get('data', [])

# query statement for loading data into warehouse
def insert_query():
    return '''
    INSERT INTO crypto.exchange (
        id,
        name,
        rank,
        percenttotalvolume,
        volumeusd,
        tradingpairs,
        socket,
        exchangeurl,
        updated_unix_millis,
        updated_utc
    )
    VALUES (
        %(exchangeId)s,
        %(name)s,
        %(rank)s,
        %(percentTotalVolume)s,
        %(volumeUsd)s,
        %(tradingPairs)s,
        %(socket)s,
        %(exchangeUrl)s,
        %(updated)s,
        %(update_dt)s
    );
    '''

# return a cursor to use for executing queries to the warehouse
def warehouse_connector(user, password, host, port, db, cursor_factory=None):
    # generates the connection url using dw credentials
    connection_url = (f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # opens a connection to the dw
    connection = psycopg2.connect(connection_url)

    # any transactions have immediate effect
    connection.autocommit = True

    # cursor allows python to execute sql commands in a dw session
    cursor = connection.cursor(cursor_factory=cursor_factory)

    return cursor

# load data into warehouse
def load_data(cursor):
    # get bitcoin data
    data = get_exchange_data()

    for d in data:
        # for each record,
        # convert the unix time under 'updated' column to utc
        # put it into a new column called 'update_dt'
        d['update_dt'] = get_utc_from_unix_time(d.get('updated'))
    
    # insert data into warehouse in batches
    p.execute_batch(cursor, insert_query(), data)

# run everything
def run():
    load_data(warehouse_connector(user, password, host, port, db))

if __name__ == '__main__':
    run()