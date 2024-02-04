"""
Matrix Crypto Display Script
Copyright (c) bigsk1 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

If you enjoy using please support my work, thanks @bigsk1_com
BTC Tips: bc1qeyzfq7qvmpmye0j9jrg5zys2vle36gm37ln8j04ahv6q9ymp8awq4ee0td
"""

import json
import curses
import time
import threading
import random
import argparse
from logging.handlers import TimedRotatingFileHandler
import logging
import requests


log_file = 'matrix_crypto.log'
logger = logging.getLogger("MatrixCryptoLogger") 
logger.setLevel(logging.INFO) 

# handler that writes log messages to a file, rotating every 10 days
handler = TimedRotatingFileHandler(log_file, when="D", interval=10, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Command-line arguments
parser = argparse.ArgumentParser(description="Matrix-style crypto ticker display.")
parser.add_argument('--speed', type=int, help='Speed of the falling text, higher is slower, default is 300.')
parser.add_argument('--color', type=str, help='Color of the falling text (e.g., green, red, white, blue, yellow, cyan, magenta).')
parser.add_argument('--bold', action='store_true', help='Display text in bold.')
parser.add_argument('--solana', action='store_true', help='Use the Solana ecosystem crypto list.')
parser.add_argument('--eth', action='store_true', help='Use the Ethereum ecosystem crypto list.')
args = parser.parse_args()

def load_cryptos(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data
if args.solana:
    config_filename = "solana_ecosystem_crypto_list.json"
elif args.eth:
    config_filename = "ethereum_ecosystem_crypto_list.json"
else:
    config_filename = "crypto_list.json"

def init_color_pair(color_name):
    color_map = {
        'red': curses.COLOR_RED,
        'green': curses.COLOR_GREEN,
        'blue': curses.COLOR_BLUE,
        'yellow': curses.COLOR_YELLOW,
        'cyan': curses.COLOR_CYAN,
        'magenta': curses.COLOR_MAGENTA,
        'white': curses.COLOR_WHITE,
    }
    color_code = color_map.get(color_name.lower(), curses.COLOR_GREEN)
    curses.start_color()
    curses.init_pair(1, color_code, curses.COLOR_BLACK)


def fetch_current_prices(crypto_list, config_name):  # Add config_name as a parameter
    crypto_ids = [crypto['id'] for crypto in crypto_list]
    base_url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': ','.join(crypto_ids), 'vs_currencies': 'usd'}
    try:
        response = requests.get(base_url, params=params, timeout=10)
        prices = response.json()
        for crypto in crypto_list:
            if crypto['id'] in prices:
                price = prices[crypto['id']]['usd']
                crypto['price'] = "{:.2f}".format(price) if price < 1000 else "{:,.0f}".format(price)
        # Use config_name in the log message to indicate which list was updated
        logger.info(f"{config_name} prices updated successfully.")
    except Exception as e:
        logger.error(f"Error fetching prices for {config_name}: {e}")


def update_prices_periodically(crypto_list, config_name, update_interval=90):
    while True:
        fetch_current_prices(crypto_list, config_name)
        time.sleep(update_interval)


def main(stdscr):
    # Dynamically choose the config file based on user input
    if args.solana:
        config_filename = "solana_ecosystem_crypto_list.json"
    elif args.eth:
        config_filename = "ethereum_ecosystem_crypto_list.json"
    else:
        config_filename = "crypto_list.json"
    
    # Load the chosen crypto list
    config = load_cryptos(config_filename)
    crypto_list = config['cryptos']

    speed = args.speed if args.speed is not None else config.get('speed', 300)
    
    color = args.color if args.color else config.get('color', 'green')

    init_color_pair(color)
    text_attr = curses.color_pair(1)
    if args.bold:
        text_attr |= curses.A_BOLD
        
    max_y, max_x = stdscr.getmaxyx()
    num_columns = len(crypto_list)
    positions = [random.randint(-max_y, 0) for _ in range(num_columns)]

    threading.Thread(target=update_prices_periodically, args=(crypto_list, config_filename, 75), daemon=True).start()

    try:
        while True:
            stdscr.clear()
            for i, crypto in enumerate(crypto_list):
                string = f"{crypto['ticker']} ${crypto.get('price', 'N/A')}"
                pos = positions[i]
                for j, char in enumerate(string):
                    y_pos = (pos + j) % (max_y + len(string))
                    x_pos = i * (max_x // num_columns)
                    try:
                        stdscr.addstr(y_pos, x_pos, char, text_attr)
                    except curses.error:
                        pass
                positions[i] += random.randint(1, 2)
            stdscr.refresh()
            time.sleep(max(0.01, speed / 1000.0))
    except KeyboardInterrupt:
        logger.info('Graceful shutdown initiated by user.')
        print("\nSuccessfully Closed. You can also use  matrix_crypto.py --help  to see all options ")

if __name__ == '__main__':
    curses.wrapper(main)