from datetime import datetime
import pytz
import requests

URL = "https://api-futures.kucoin.com"

symbols_list_response = requests.get(f"{URL}/api/v1/contracts/active")
symbols_list = symbols_list_response.json()["data"]

# print(symbols_list)


def first_dict():
    main_dict = {}
    symbol_names = []
    symbol_prices = []
    funding_rates = []
    funding_times = []

    for symbol in symbols_list:
        symbol_name = symbol["symbol"]
        symbol_names.append(symbol_name)

        symbol_price = symbol["indexPrice"]
        symbol_prices.append(symbol_price)

        funding_time = datetime.fromtimestamp(int(symbol["nextFundingRateTime"]) / 1000,
                                              tz=pytz.timezone('America/Toronto')).strftime('%Y-%m-%d %H:%M:%S')
        funding_times.append(funding_time)

        funding_response = requests.get(f"{URL}/api/v1/funding-rate/{symbol_name}/current")
        funding_data = funding_response.json()["data"]
        funding_rate = funding_data["value"]
        funding_rates.append(funding_rate)

    for i in range(0, len(symbol_names)):
        main_dict[symbol_names[i]] = symbol_prices[i]
        main_dict[symbol_names[i]] = funding_rates[i]
        main_dict[symbol_names[i]] = funding_times[i]

    return main_dict


print(first_dict())
