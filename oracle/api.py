import requests
import os

API_KEY = os.environ.get("API_KEY")

# See API documentation https://docs.kaiko.com/#spot-price
def get_request_headers():
    return {
            'Accept': "application/json",
            'X-Api-Key': API_KEY
        }


def get_params(cont_token=None):
    # For first request (i.e,, no cont_token), include page_size; subsequent requests have
    # page_size encoded in continuation token
    return {"continuation_token": cont_token} if cont_token else {'page_size': 1000}


def make_request(cont_token=None):
    return requests.get(
        "https://us.market-api.kaiko.io/v1/data/trades.v1/exchanges/spots/recent",
        headers=get_request_headers(),
        params=get_params(cont_token)
    )

def get_price(data): 
    return (data.get('data', {}).get('exchange'), (data.get('data', {}).get('instrument'), data.get('data', {}).get('price')))


def parse_responses(responses):
    return [
        get_price(datum) 
            for resp in responses
            for datum in resp.get('data', []) 
            if datum.get('result') == 'success'
        ]


def make_resp_dict(resp_lst):
    resp_dict = {}
    for resp in resp_lst: 
        resp_dict[resp[0]] = resp_dict.get(resp[0], []) + [resp[1]]
    return resp_dict


def fetch_and_parse_price_data():
    """"""
    response = make_request()
    resp_list = [response.json()]
    while response.json().get('continuation_token'):
        response = make_request(response.json().get('continuation_token'))
        resp_list.append(response.json())
    # return make_resp_dict(parse_responses(resp_list))
    return parse_responses(resp_list)


def make_michelson(parsed_resp_list):
    # for (list (pair string string))
    pairs = "; ".join([f'(Pair "{tup[1][0]}" "{tup[1][1]}")' for tup in parsed_resp_list[:100]])
    return f"{{ {pairs} }}"