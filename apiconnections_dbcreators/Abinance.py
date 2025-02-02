import sqlite3
import requests
from binance.client import Client
import ccxt
import pytz
from decimal import Decimal, ROUND_DOWN
import time
from datetime import datetime, timedelta
import json
import os
import asyncio
import aiohttp

# BINANCE
# ----------------------------------------------------------------------------------
api_key = 'Vh5wNlaNBMwoqmuur9jTQxid4sROuL6zCPfyYJOgRBg58uY9L80qfmj8u8modSbP'
api_secret = 'DhoWPQvBLmx7pUBeEQXYnnpQt6WJWhNILUDjm5RrGoXkY36hOjVJTHVHshrbAcww'
client = Client(api_key, api_secret)

def create_futures_info_dict(info_all_futures_tickers):
    symbols_dict = {}
    for ticker in info_all_futures_tickers:
        symbol = ticker['symbol']
        lastPrice = float(ticker['lastPrice'])



        symbols_dict[symbol] = [lastPrice]
    return symbols_dict


exchange = ccxt.binance({
    'enableRateLimit': True,
})


def add_funding_rate(response,futures_info_dict):
    for i in response:
        fundingRate = 100 * float(i['lastFundingRate'])
        fundingTime_ms = int(i['nextFundingTime'])
        nowTime_ms = int(i['time'])
        time_diff_ms = fundingTime_ms - nowTime_ms
        time_diff_seconds = time_diff_ms / 1000
        time_diff_datetime = timedelta(seconds=abs(time_diff_seconds))
        toronto_timezone = pytz.timezone('America/Toronto')
        now_toronto_time = datetime.now(toronto_timezone)
        next_funding_toronto_time = now_toronto_time + time_diff_datetime
        seconds_to_round = next_funding_toronto_time.second + next_funding_toronto_time.microsecond / 1e6
        if seconds_to_round >= 30:
            next_funding_toronto_time += timedelta(minutes=1)
        next_funding_toronto_time = next_funding_toronto_time.replace(second=0, microsecond=0)
        till_next_funding = next_funding_toronto_time.strftime('%Y-%m-%d %H:%M:%S')
        symbol = i['symbol']
        if symbol in futures_info_dict:
            futures_info_dict[symbol].append(fundingRate)
            futures_info_dict[symbol].append(till_next_funding)
    return futures_info_dict

response = exchange.fapiPublicGetPremiumIndex()
info_all_futures_tickers = client.futures_ticker()
futures_info_dict = create_futures_info_dict(info_all_futures_tickers)
main_trade_dict = add_funding_rate(response, futures_info_dict)
print(main_trade_dict)

