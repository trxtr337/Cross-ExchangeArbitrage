import asyncio
import aiohttp

URL = "https://api.bitget.com"

API_KEY = ""
API_SECRET = ""


async def first_dict():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/v2/mix/market/tickers?productType=USDT-FUTURES") as response:
            ticker_info = await response.json()
            ticker_dict = {}

            for ticker in ticker_info["data"]:
                ticker_dict[ticker["symbol"]] = [float(ticker["lastPr"]), float(ticker["fundingRate"])]

            print(ticker_dict)

    return ticker_dict

asyncio.run(first_dict())
