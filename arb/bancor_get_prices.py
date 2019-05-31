#!/usr/bin/env python3

import requests        # for making http requests to binance
import json            # for parsing what binance sends back to us
import time            # for sleep()

def bancor_get_pairs():
    
    url = 'https://api.bancor.network/0.1/currencies/convertiblePairs'

    response = requests.get(url)
    #print(response.url)
    parsedResp = json.loads( response.text )
    #print(data)
    return parsedResp['data']


def bancor_get_price(fromCurr, toCurr, toAmount):

    wei = 1000000000000000000
    url = 'https://api.bancor.network/0.1/currencies/{}/value'.format(fromCurr)
    
    response = requests.get(url, params = {'toCurrencyCode': toCurr, 'toAmount' : toAmount*wei} )
    #print(response.url)
    parsedResp = json.loads( response.text )
    #print(parsedResp)
    return ( int(parsedResp['data']) / ( wei * 0.0 ) )

def uniswap_get_pairs():
    #https://uniswap-analytics.appspot.com/api/v1/ticker?exchangeAddress=
    with open('uniswap_addr.json') as f:
        data = json.load(f)
        for 

if __name__ == "__main__":

    pairs = bancor_get_pairs()
    amount = 100
    for fromCurr, toCurr in pairs.items():
        if len(fromCurr) > 3 and fromCurr[-3:] == 'BNT':  # pass internal token like KINBNT
            continue
        try:
            price = bancor_get_price (fromCurr, toCurr, amount)
            print ( 'for {} {} you will get {} {}'.format(price, fromCurr, amount, toCurr) )
            #time.sleep(2)
        except Exception: 
            pass
