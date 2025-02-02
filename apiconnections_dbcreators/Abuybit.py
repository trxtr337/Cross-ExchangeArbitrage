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


# BYBIT
async def create_futures_info_dict_bybit():
    url = "https://api.bybit.com/v2/public/tickers"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if response.status == 200 and data['ret_code'] == 0:
                info_all_futures_tickers = data['result']
                symbols_dict = {}
                for ticker in info_all_futures_tickers:
                    symbol = ticker['symbol']
                    lastPrice = float(ticker['last_price'])
                    volume = float(ticker['volume_24h'])
                    fundingRate = 100*float(ticker['funding_rate'])
                    priceChangePercent = 100*float(ticker['price_24h_pcnt'])
                    nextFundingTimeUTC = ticker['next_funding_time']

                    # Конвертируем время следующего фондирования из UTC в местное время Торонто
                    utc_zone = pytz.timezone('UTC')
                    toronto_zone = pytz.timezone('America/Toronto')
                    if nextFundingTimeUTC:  # Проверяем, что строка не пуста
                        nextFundingTime = utc_zone.localize(
                            datetime.strptime(nextFundingTimeUTC, '%Y-%m-%dT%H:%M:%SZ')).astimezone(toronto_zone)
                        nextFundingTimeFormatted = nextFundingTime.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        nextFundingTimeFormatted = 'N/A'

                    # Вычисляем объем в USD (здесь используется volume_24h)
                    volumeInUSD = lastPrice * volume

                    symbols_dict[symbol] = [lastPrice, volumeInUSD, priceChangePercent,fundingRate, nextFundingTimeFormatted ]
                print(symbols_dict)
                return symbols_dict
            else:
                print("Ошибка при получении данных с Bybit")
                return {}

if __name__ == '__main__':
    asyncio.run(create_futures_info_dict_bybit())