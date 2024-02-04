import requests
import json

def fetch_solana_ecosystem_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'category': 'solana-ecosystem',
        'order': 'market_cap_desc',
        'per_page': 20,  # Adjust the number of coins as needed
        'page': 1
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch Solana ecosystem coins: {response.status_code}")
        return []

def save_crypto_list(crypto_data, filename="solana_ecosystem_crypto_list.json", speed=300, color="green"):
    config = {
        "speed": speed,
        "color": color,
        "cryptos": [{
            "id": crypto['id'],
            "ticker": crypto['symbol'].upper(),
            "name": crypto['name']
        } for crypto in crypto_data]
    }
    
    with open(filename, 'w') as file:
        json.dump(config, file, indent=4)

    print(f"Configuration saved to {filename}")

if __name__ == '__main__':
    solana_cryptos = fetch_solana_ecosystem_cryptos()
    save_crypto_list(solana_cryptos)

