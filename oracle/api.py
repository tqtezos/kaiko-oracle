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
        resp.get('query', {}).get('instrument'): (
            resp.get('query', {}).get('exchange'), 
            (head(resp.get('data', [])) or {}).get('timestamp'), 
            (head(resp.get('data', [])) or {}).get('price')
            )
        for resp in responses
    }
    # return [
    #     (resp.get('query', {}).get('') get_price(datum) 
    #         for resp in responses
    #         for datum in resp.get('data', []) 
    #         if resp.get('result') == 'success'
    #     ]


def make_resp_dict(resp_lst):
    resp_dict = {}
    for resp in resp_lst: 
        resp_dict[resp[0]] = resp_dict.get(resp[0], []) + [resp[1]]
    return resp_dict


def fetch_and_parse_price_data():
    """"""
    resp_list = []
    for instrument in ['xtz-usd', 'xtz-btc']:
        response = make_request(instrument)
        resp_list.append(response.json())
        # return make_resp_dict(parse_responses(resp_list))
    return parse_responses(resp_list)


def make_michelson(parsed_resp_list):
    # for (list (pair string string))
    pairs = "; ".join([f'(Pair "{tup[1][0]}" "{tup[1][1]}")' for tup in parsed_resp_list[:100]])
    return f"{{ {pairs} }}"

def make_string_pairs(parsed_resp_list):
    return [[tup[1][0],tup[1][1]] for tup in parsed_resp_list]