import asyncio
import aiohttp
from datetime import datetime

import pytz


async def second_upd(future_info):
    base_url = "https://contract.mexc.com/api/v1"
    ticker_url = f"{base_url}/contract/ticker"


    async with aiohttp.ClientSession() as session:
        async with session.get(ticker_url) as ticker_response:
            if ticker_response.status == 200:
                ticker_data = await ticker_response.json()
                info_all_futures_tickers = ticker_data['data']

                for ticker in info_all_futures_tickers:
                    symbol = ticker['symbol']
                    lastPrice = float(ticker['lastPrice'])
                    fundingRate = 100 * float(ticker['fundingRate'])
                    future_info[symbol] = {
                        'lastPrice': lastPrice,
                        'fundingRate': fundingRate,
                        'nextFundingTime': future_info[symbol]['nextFundingTime']
                    }

    return future_info

async def fetch_funding_rate(session, url, semaphore, symbols_dict, symbol):
    async with semaphore:
        async with session.get(url) as response:
            #print(response)
            if response.status == 200:
                data = await response.json()
                if data['success']:
                    funding_time = datetime.fromtimestamp(int(data['data']['nextSettleTime']) / 1000,
                                                          tz=pytz.timezone('America/Toronto')).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    symbols_dict[symbol]['nextFundingTime'] = funding_time




async def create_futures_info_dict_bybit():
    base_url = "https://contract.mexc.com/api/v1"
    ticker_url = f"{base_url}/contract/ticker"
    symbols_dict = {}
    semaphore = asyncio.Semaphore(20)

    async with aiohttp.ClientSession() as session:
        async with session.get(ticker_url) as ticker_response:
            if ticker_response.status == 200:
                ticker_data = await ticker_response.json()
                info_all_futures_tickers = ticker_data['data']

                for ticker in info_all_futures_tickers:
                    symbol = ticker['symbol']
                    lastPrice = float(ticker['lastPrice'])
                    fundingRate = 100 * float(ticker['fundingRate'])
                    symbols_dict[symbol] = {
                        'lastPrice': lastPrice,
                        'fundingRate': fundingRate,
                    }

                tasks = [
                    fetch_funding_rate(session, f"{base_url}/contract/funding_rate/{symbol}", semaphore, symbols_dict,
                                       symbol) for symbol in symbols_dict]

                # Process tasks in chunks of 20
                chunks = [tasks[i:i + 20] for i in range(0, len(tasks), 20)]
                for chunk in chunks:
                    await asyncio.gather(*chunk)
                    await asyncio.sleep(2)  # Wait for 2 seconds before sending the next batch of requests
            else:
                print("Ошибка при получении данных с MEXC")

    return symbols_dict


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Получаем начальную информацию
    future_info = loop.run_until_complete(create_futures_info_dict_bybit())
    future_info_upd = asyncio.run(second_upd(future_info))
    print(future_info_upd)