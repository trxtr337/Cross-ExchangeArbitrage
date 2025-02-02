import asyncio
import aiohttp
from datetime import datetime
import pytz
import json  # Import json library


async def get_funding():
    async with aiohttp.ClientSession() as session:
        funding_url = "https://api.hbdm.com/linear-swap-api/v1/swap_batch_funding_rate"
        async with session.get(funding_url) as response:
            # Manually decode the response content as JSON
            response_text = await response.text()  # Read the response as text
            try:
                funding_response_data = json.loads(response_text)  # Try to parse text as JSON
            except json.JSONDecodeError:
                print("Failed to decode JSON")
                return
            funding_response_data = funding_response_data["data"]

            tasks = [get_price(session, symbol["symbol"] + "-USDT") for symbol in funding_response_data if
                     symbol["funding_rate"] is not None]
            prices = await asyncio.gather(*tasks)

            for symbol, price in zip(funding_response_data, prices):
                if symbol["funding_rate"] is not None:
                    symbol_name = symbol["symbol"] + "USDT"
                    funding_rate = symbol["funding_rate"]
                    funding_time = datetime.fromtimestamp(int(symbol["funding_time"]) / 1000,
                                                          tz=pytz.timezone('America/Toronto')).strftime(
                                                          '%Y-%m-%d %H:%M:%S')
                    print(symbol_name, funding_rate, funding_time, price)


async def get_price(session, symbol):
    # await asyncio.sleep(0.1)
    price_url = f"https://api.hbdm.com/linear-swap-ex/market/trade?contract_code={symbol}"
    async with session.get(price_url) as response:
        price_data = await response.json()

        # Check for 'tick' key in the response and if the status is 'ok'
        if 'tick' in price_data and price_data.get('status') == 'ok':
            price = price_data["tick"]["data"][0]["price"]
            return price
        else:
            # Handle error or missing 'tick' key
            err_msg = price_data.get('err-msg', 'No tick data')
            print(f"Error fetching price for {symbol}: {err_msg}")
            await get_price(session, symbol)
            return None


asyncio.run(get_funding())
