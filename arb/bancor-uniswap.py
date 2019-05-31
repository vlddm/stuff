#!/usr/bin/env python3

import requests        # for making http requests to binance
import json            # for parsing what binance sends back to us
import time            # for sleep()
import traceback

from uniswap import UniswapWrapper


def bancor_get_pairs():
    
    url = 'https://api.bancor.network/0.1/currencies/convertiblePairs'

    response = requests.get(url)
    #print(response.url)
    parsedResp = json.loads( response.text )
    #print(data)
    return parsedResp['data']


def bancor_get_price(fromCurr, toCurr, amount):

    wei = 1000000000000000000
    url = 'https://api.bancor.network/0.1/currencies/{}/value'.format(fromCurr)
    
    response = requests.get(url, params = {'toCurrencyCode': toCurr, 'toAmount' : amount * wei} )
    #print(response.url)
    parsedResp = json.loads( response.text )
    #print(parsedResp)
    return ( int(parsedResp['data']) / ( wei * 1.0 ) )

def uniswap_get_pairs():
    eth = "0x0000000000000000000000000000000000000000"
    bat = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"
    dai = "0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359"
    print ( uniswap_wrapper.get_eth_token_output_price(uniswap_wrapper.token_address_from_symbol['DAI'], 1*10**18)/10**18 )


if __name__ == "__main__":
    uniswap_wrapper = UniswapWrapper('3a1076bf45ab87712ad64ccb3b10217737f7faacbf2872e88fdd9a537d8fe266','0xc2d7cf95645d33006175b78989035c7c9061d3f9', provider='https://mainnet.infura.io/v3/__apikey__here')
    bancor_pairs = bancor_get_pairs()
    amount = 1
    for fromCurr, toCurr in bancor_pairs.items():
        if len(fromCurr) > 3 and fromCurr[-3:] == 'BNT':  # pass internal token like KINBNT
            continue
        try:
            #print ( 'getting {} from bancor'.format(fromCurr) )
            bancor_price = bancor_get_price (fromCurr, toCurr, amount)
            if fromCurr == 'ETH':
                ethbnt = bancor_price
                symbol = 'BNT'
            else:
                symbol = fromCurr
                bancor_price = ethbnt / bancor_price
            uniswap_price = uniswap_wrapper.get_eth_token_output_price(uniswap_wrapper.token_address_from_symbol[symbol], 1*10**18)/10**18
            print ( '{} bancor: {} uniswap: {}, difference {}'.format(symbol, bancor_price, uniswap_price, int( 100* (bancor_price-uniswap_price)/uniswap_price ) ) )
            #time.sleep(2)
        except Exception as e: 
            #traceback.print_exc()
            pass
