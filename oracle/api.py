import requests
import os
from datetime import datetime, timedelta
from decimal import Decimal


API_KEY = os.environ.get("API_KEY")

def tail(lst):
    try: 
        return lst[-1]
    except IndexError:
        return None


# See API documentation https://docs.kaiko.com/#recent-vwap-alpha-release
def get_request_headers():
    return {
            'Accept': "application/json",
            'X-Api-Key': API_KEY
        }


def make_request(instrument, exchange, cont_token=None):
    # Passing params in url instead of param dict to keep start_time from url encoding
    # as recommended by author of requests lib :/ https://stackoverflow.com/a/23497903
    start_time = (datetime.utcnow().replace(microsecond=0) - timedelta(hours=1)).isoformat() + "Z"
    url = f"https://us.market-api.kaiko.io/v1/data/trades.v1/exchanges/{exchange}/spot/{instrument}/aggregations/vwap?interval=1m&start_time={start_time}&page_size=1000"
    print(url)
    return requests.get(
        url,
        headers=get_request_headers()
    )


def btc_to_satoshi(btc):
    return int(Decimal(btc[:25]).shift(8).to_integral())


def usd_to_usc(usd):
    return int(Decimal(usd[:25]).shift(2).to_integral())


def raw_to_int(raw_price):
    return int(Decimal(raw_price[:25]).to_integral())


def convert_price(raw_price, instrument):
    return {
        'xtz-btc': btc_to_satoshi(raw_price),
        'xtz-usd': usd_to_usc(raw_price),
    }.get(instrument, raw_to_int(raw_price))


def parse_price(resp):
    raw_price = (tail(resp.get('data', [])) or {}).get('price')
    return (
        convert_price(raw_price, resp.get('query', {}).get('instrument'))
            if raw_price is not None
            else raw_price)


def convert_ts(timestamp):
    return None if timestamp is None else datetime.datetime.fromtimestamp(int(timestamp / 1000)).isoformat()


def parse_response(resp):
    return [
            convert_ts((tail(resp.get('data', [])) or {}).get('timestamp')), 
            parse_price(resp)
        ]


def fetch_and_parse_price_data(instrument, exchange="krkn"):
    """"""
    response = make_request(instrument, exchange)
    return parse_response(response.json())
