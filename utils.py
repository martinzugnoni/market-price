import time
import locale
import requests

BASE_URL = "https://api.mercadolibre.com"


def search_products_in_mercadolibre(url_args):
    limit = 50
    offset = 0
    all_results = []
    extra_url_args = "&".join([f"{k}={v}" for k, v in url_args.items()])
    while True:
        url = f"{BASE_URL}/sites/MLA/search?limit={limit}&offset={offset}&{extra_url_args}#json"
        response = requests.get(url)
        if response.status_code != 200:
            print(response.content)
            break
        results = response.json()["results"]
        if not results:
            break
        all_results += results
        offset += limit
        if offset > 1000:
            # max allowed without token
            break
    return all_results


def get_precio_dolar(blue=False, tipo='compra'):
    dolarsi_url = 'https://www.dolarsi.com/api/api.php?type=valoresprincipales'
    response = requests.get(dolarsi_url)
    key = 'Dolar Blue' if blue else 'Dolar Oficial'
    doc = [doc for doc in response.json() if doc['casa']['nombre'] == key][0]
    return float(doc['casa'][tipo].replace(',', '.'))


def currency_format(value, locale_name='en_US'):
    locale.setlocale(locale.LC_ALL, locale_name)
    return locale.format_string('%d', value, grouping=True)