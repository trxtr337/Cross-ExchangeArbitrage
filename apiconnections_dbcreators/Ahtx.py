from datetime import datetime
import pytz
import requests
import asyncio
# import aiohttp


async def get_funding():
    first_dict = {}

    funding_response = requests.get("https://api.hbdm.com/linear-swap-api/v1/swap_batch_funding_rate")
    funding_response_data = funding_response.json()["data"]
    # print(funding_response_data)
    for symbol in funding_response_data:
        if symbol["funding_rate"] is not None:
            symbol_name = symbol["symbol"] + "USDT"
            funding_rate = symbol["funding_rate"]
            funding_time = datetime.fromtimestamp(int(symbol["funding_time"]) / 1000,
                                                  tz=pytz.timezone('America/Toronto')).strftime('%Y-%m-%d %H:%M:%S')
            price_data = await get_price(symbol["symbol"] + "-USDT")


async def get_price(symbol):
    price_response = requests.get(f"https://api.hbdm.com/linear-swap-ex/market/trade?contract_code={symbol}")
    price_data = price_response.json()["tick"]["data"][0]["price"]
    return price_data


asyncio.run(get_funding())
# asyncio.run(get_price("BTC-USDT"))
