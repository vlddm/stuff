#!/usr/bin/env python3

import requests        # for making http requests to binance
import json            # for parsing what binance sends back to us
import pandas as pd    # for storing and manipulating the data we get back

import argparse, time, calendar

def get_bars(symbol, begin, interval = '1m', limit = 1000):
    
    url = 'https://api.binance.com/api/v1/klines'
    payload = {'symbol': symbol, 'startTime': int(begin)*1000, 
               'interval': interval, 'limit': limit }
    response = requests.get(url, params = payload)
    #print(response.url)
    data = json.loads( response.text )
    #print(data)
    df = pd.DataFrame(data)
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume',
                 'close_time', 'qav', 'num_trades',
                 'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [int(x/1000.0) for x in df.open_time]
    return df

def get_csv(symbol, startTime):
    
    finishTime = time.gmtime() # Now (UTC)
    date_fmt = '%Y-%m-%d-%H:%M:%S'
    filename = symbol + '_' + time.strftime(date_fmt, startTime) + '_' + time.strftime(date_fmt, finishTime) + '.csv'
    print ("writing to " + filename)
    
    
    startTime = calendar.timegm(startTime) # epoch (UTC)
    finishTime = calendar.timegm(finishTime)
    header = True
    limit = 1000       # 1000 records per requests
    step = limit * 60  # iterate in seconds

    with open(filename, 'w') as csvfile:
    
        for begin in range (startTime, finishTime, step):

            df = get_bars(symbol, begin, limit=limit)

            df.to_csv ( path_or_buf = csvfile, index = True, index_label = 'timestamp', 
                        header = header, columns = ['open', 'high', 'low', 'close', 'volume'] ) 
            header = False       # Write header only once

            percentDone = int( 100 * ( startTime - begin ) / ( startTime - finishTime ) )
            print ( "{} downloading done: {}%".format(symbol, percentDone) )
            time.sleep ( 2 )     # sleep 2 seconds between requests

def valid_date(s):
    try:
        return time.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Binance history data downloader")
    parser.add_argument("-s", "--symbol", dest='symbol', required=True,
                        help="Symbol to get, like ETHUSDT")
    parser.add_argument("-t", "--start-time", dest='startTime', required=True, type=valid_date,
                        help="Beggining of the interval (YYYY-MM-DD), like 2019-05-04")

    args = parser.parse_args()
    get_csv(args.symbol, args.startTime)
