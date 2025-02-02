import asyncio
import aiohttp
from datetime import datetime, timedelta
import pytz

URL = "https://api-futures.kucoin.com"

async def fetch_funding_rate(session, symbol_name):
    async with session.get(f"{URL}/api/v1/funding-rate/{symbol_name}/current") as response:
        funding_data = await response.json()
        print(symbol_name)
        print(funding_data)
        if funding_data["code"] == '200000':
            # Предполагается, что данные о времени и гранулярности доступны в ответе
            time_point = funding_data["data"]["timePoint"] / 1000  # Переводим в секунды
            granularity = funding_data["data"]["granularity"] / 1000  # Переводим в секунды
            utc_time = datetime.utcfromtimestamp(time_point + granularity)
            toronto_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Toronto'))
            next_funding_time = toronto_time.strftime('%Y-%m-%d %H:%M:%S')
            return funding_data["data"]["value"], next_funding_time

async def fetch_symbols_list():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/v1/contracts/active") as response:
            symbols_list = await response.json()
            return symbols_list["data"]

async def first_dict_async():
    symbols_list = await fetch_symbols_list()
    main_dict = {}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_funding_rate(session, symbol["symbol"]) for symbol in symbols_list]
        results = await asyncio.gather(*tasks)

        for i, symbol in enumerate(symbols_list):
            symbol_name = symbol["symbol"]
            symbol_price = symbol["indexPrice"]
            funding_rate, next_funding_time = results[i] if results[i] else (None, None)
            print(symbol)

            # Записываем информацию в словарь
            if funding_rate is not None and next_funding_time is not None:
                fr = 100* funding_rate
                main_dict[symbol_name] = {
                    'price': symbol_price,
                    'funding_rate': fr,
                    'next_funding_time': next_funding_time,
                }

    return main_dict

# Запускаем асинхронную функцию и печатаем результат
async def main():
    result = await first_dict_async()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
