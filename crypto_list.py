# Run this file to pull the top 20 cryptocurrencies, formatted with their id, ticker, and name, ready for use

import requests
import json

def fetch_top_crypto(limit=20):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': False,
        'price_change_percentage': '7d'
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch cryptocurrencies")
        return []

def save_crypto_list(crypto_data, filename="crypto_list.json"):
    config = {
        "speed": 300,
        "color": "green",
        "cryptos": []
    }
    
    for crypto in crypto_data:
        config["cryptos"].append({
            "id": crypto['id'],
            "ticker": crypto['symbol'].upper(), 
            "name": crypto['name']
        })
    
    with open(filename, 'w') as file:
        json.dump(config, file, indent=4)
        
    print(f"Configuration saved to {filename}")


if __name__ == '__main__':
    top_cryptos = fetch_top_crypto(limit=20)
    save_crypto_list(top_cryptos)