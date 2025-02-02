import asyncio
from datetime import datetime

import aiohttp
import pytz


async def fetch_funding_rate(session, inst_id, current_price):
    url_funding_rate = f"https://www.okx.com/api/v5/public/funding-rate?instId={inst_id}"
    async with session.get(url_funding_rate) as response:
        data_funding_rate = await response.json()
        if data_funding_rate['code'] == '0':
            # Добавляем текущую цену в данные фандинг-ставки
            return {**data_funding_rate['data'][0], 'current_price': current_price}
        else:
            print(f"Ошибка при получении фандинг-ставки для {inst_id}: {data_funding_rate['msg']}")
        return None

async def get_mark_price(session):
    url_mark_price = "https://www.okx.com/api/v5/public/mark-price?instType=SWAP"
    async with session.get(url_mark_price) as response:
        data_mark_price = await response.json()
        if data_mark_price['code'] == '0':
            # Возвращаем данные в виде словаря для удобства доступа
            return {item['instId']: item for item in data_mark_price['data']}
        else:
            return None

async def get_futures_ticker_info_okx():
    async with aiohttp.ClientSession() as session:
        mark_prices = await get_mark_price(session)
        if mark_prices:
            tasks = []
            for inst_id, mark_price_info in mark_prices.items():
                current_price = mark_price_info['markPx']  # Текущая маркет-цена
                # Передаем текущую цену как параметр
                task = fetch_funding_rate(session, inst_id, current_price)
                tasks.append(task)
            funding_rates_info = await asyncio.gather(*tasks)
            funding_rates_info = [item for item in funding_rates_info if item is not None]
            return funding_rates_info
        else:
            print("Ошибка при получении маркет-цен")
            return []



async def main():
    funding_rates = await get_futures_ticker_info_okx()
    result = {}

    for item in funding_rates:
        symbol = item['instId'].replace('-', '')[:-4]
        current_price = float(item['current_price'])
        funding_rate = 100*float(item['fundingRate'])
        # Преобразуем fundingTime в формат даты и времени
        funding_time = datetime.fromtimestamp(int(item['fundingTime']) / 1000,
                                              tz=pytz.timezone('America/Toronto')).strftime('%Y-%m-%d %H:%M:%S')
        # Сохраняем в итоговом словаре
        result[symbol] = [current_price, funding_rate, funding_time]
        print(item["fundingTime"])

    # print(result)

asyncio.run(main())