from datetime import datetime
import pytz
import requests

API_KEY = "bf531b6d1a90f0474431d620c0aa95bd"
API_SECRET = "4396a577a5dffe1a161f85ca25ad938595978aca107baf6e2708649b58b2bdfc"

URL = "https://api.gateio.ws/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

futures_info_response = requests.get(f"{URL}/futures/usdt/contracts", headers=headers)
futures_info = futures_info_response.json()


def main_dict():
    funding_dict = {}

    for symbol in futures_info:
        last_price = float(symbol["last_price"])
        funding_rate = float(symbol["funding_rate"])
        funding_time = datetime.fromtimestamp(int(symbol["funding_next_apply"]),
                                              tz=pytz.timezone('America/Toronto')).strftime('%Y-%m-%d %H:%M:%S')

        funding_dict[symbol["name"].replace("_", "")] = [last_price,
                                                         funding_rate,
                                                         funding_time]

    return funding_dict


print(main_dict())
