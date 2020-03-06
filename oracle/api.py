import requests
import os
from datetime import datetime, timedelta

API_KEY = os.environ.get("API_KEY")

def head(lst):
    try: 
        return lst[0]
    except IndexError:
        return None

# See API documentation https://docs.kaiko.com/#recent-vwap-alpha-release
def get_request_headers():
    return {
            'Accept': "application/json",
            'X-Api-Key': API_KEY
        }


def make_request(instrument, exchange="krkn", cont_token=None):
    # Passing params in url instead of param dict to keep start_time from url encoding
    # as recommended by author of requests lib :/ https://stackoverflow.com/a/23497903
    start_time = (datetime.utcnow().replace(microsecond=0) - timedelta(days=30)).isoformat() + "Z"
    
    return requests.get(
        f"https://us.market-api.kaiko.io/v1/data/trades.v1/exchanges/{exchange}/spot/{instrument}/aggregations/vwap?interval=1m&start_time={start_time}",
        headers=get_request_headers()
    )

def get_price(data): 
    return (data.get('data', {}).get('exchange'), (data.get('data', {}).get('instrument'), data.get('data', {}).get('price'), data.get('data')))


def parse_responses(responses):
    return {
        resp.get('query', {}).get('instrument'): [
            (head(resp.get('data', [])) or {}).get('timestamp'), 
            (head(resp.get('data', [])) or {}).get('price')
        ]
        for resp in responses
    }


def fetch_and_parse_price_data():
    """"""
    resp_list = []
    for instrument in sorted(['xtz-btc', 'xtz-usd']):
        response = make_request(instrument)
        resp_list.append(response.json())
    return parse_responses(resp_list)
