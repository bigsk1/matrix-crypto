import json
import curses
import time
import threading
import random
import argparse
from logging.handlers import TimedRotatingFileHandler
import logging
import requests

# User-configurable settings
SETTINGS = {
    'ANIMATION_SPEED': 0.01,  # Lower is faster, higher is slower. This is the delay between frames in seconds.
    'BACKGROUND_PATTERN': [1, 2, 3, 1],  # Gap widths pattern.
    'BACKGROUND_CHARS': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/',
    'CRYPTO_DISPLAY_COUNT': 3,  # Maximum number of crypto prices displayed simultaneously.
    'CRYPTO_DISPLAY_CHANCE': 0.13,  # Chance of new crypto display appearing each frame.
    'FADE_LENGTH': 0,  # Length of fade effect at top and bottom in number of characters.
    'BACKGROUND_INTENSITY_LEVELS': 5,  # Number of intensity levels for background.
    'CRYPTO_FALL_SPEED_RANGE': (0.12, 0.16),  # Min and max fall speed for crypto displays in seconds.
    'BACKGROUND_CHANGE_CHANCE': 0.5,  # Chance of a background character changing each update.
    'BACKGROUND_FALL_SPEED_RANGE': (0.06, 0.1),  # Min and max fall speed for background characters in seconds.
    'BACKGROUND_COLUMN_LENGTH_RANGE': (0.3, 0.6),  # Min and max length of background columns as a fraction of screen height.
    'BACKGROUND_COLUMN_GAP_RANGE': (0.2, 0.4),  # Min and max gap between columns as a fraction of screen height.
    'LEAD_CHAR_COLOR': curses.COLOR_WHITE,  # Color of the leading character in each column.
    'LEAD_CHAR_CHANCE': 1,  # Chance of a new leading character appearing when the column updates.
    'CRYPTO_COLOR': 'white',  # Default color for crypto tickers
}

COLOR_MAP = {
    'red': curses.COLOR_RED,
    'green': curses.COLOR_GREEN,
    'blue': curses.COLOR_BLUE,
    'yellow': curses.COLOR_YELLOW,
    'cyan': curses.COLOR_CYAN,
    'magenta': curses.COLOR_MAGENTA,
    'white': curses.COLOR_WHITE,
}

log_file = 'matrix_crypto.log'
logger = logging.getLogger("MatrixCryptoLogger")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(log_file, when="D", interval=10, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Update argument parser
parser = argparse.ArgumentParser(description="Matrix-style crypto ticker display.")
parser.add_argument('--bg-color', type=str, default='green', help='Color of the falling background text (e.g., green, red, white, blue, yellow, cyan, magenta).')
parser.add_argument('--crypto-color', type=str, help='Color of the crypto tickers (e.g., white, yellow, cyan). Overrides SETTINGS["CRYPTO_COLOR"].')
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

def fetch_current_prices(crypto_list, config_name):
    crypto_ids = [crypto['id'] for crypto in crypto_list]
    base_url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': ','.join(crypto_ids), 'vs_currencies': 'usd'}
    try:
        response = requests.get(base_url, params=params, timeout=20)
        prices = response.json()
        for crypto in crypto_list:
            if crypto['id'] in prices:
                price = prices[crypto['id']]['usd']
                crypto['price'] = "{:.2f}".format(price) if price < 1000 else "{:,.0f}".format(price)
        logger.info(f"{config_name} prices updated successfully.")
    except Exception as e:
        logger.error(f"Error fetching prices for {config_name}: {e}")

def update_prices_periodically(crypto_list, config_name, update_interval=120):
    while True:
        fetch_current_prices(crypto_list, config_name)
        time.sleep(update_interval)

def init_color_pairs(bg_color, crypto_color):
    curses.start_color()
    curses.use_default_colors()
    
    bg_color_code = COLOR_MAP.get(bg_color.lower(), curses.COLOR_GREEN)
    crypto_color_code = COLOR_MAP.get(crypto_color.lower(), curses.COLOR_WHITE)
    
    curses.init_pair(1, bg_color_code, -1)
    curses.init_pair(9, curses.COLOR_WHITE, -1)  # Lead character color
    curses.init_pair(10, crypto_color_code, -1)  # Crypto ticker color

class MatrixColumn:
    def __init__(self, height):
        self.height = height
        self.length = int(random.uniform(*SETTINGS['BACKGROUND_COLUMN_LENGTH_RANGE']) * height)
        self.chars = [' '] * height
        self.intensities = [1] * height
        self.speed = random.uniform(*SETTINGS['BACKGROUND_FALL_SPEED_RANGE'])
        self.counter = 0
        self.top = -self.length  # Start above the screen
        self._initialize_column()

    def _initialize_column(self):
        for i in range(self.length):
            self.chars[i] = random.choice(SETTINGS['BACKGROUND_CHARS'])
            self.intensities[i] = random.randint(1, SETTINGS['BACKGROUND_INTENSITY_LEVELS'])

    def update(self, dt):
        self.counter += dt
        if self.counter >= self.speed:
            self.counter = 0
            self.top += 1
            if self.top >= 0:
                # Shift characters down
                self.chars.pop()
                self.intensities.pop()
                # Add new character at the top
                self.chars.insert(0, random.choice(SETTINGS['BACKGROUND_CHARS']))
                self.intensities.insert(0, random.randint(1, SETTINGS['BACKGROUND_INTENSITY_LEVELS']))
            
            # Randomly change some characters
            for i in range(min(self.length, self.height)):
                if random.random() < SETTINGS['BACKGROUND_CHANGE_CHANCE']:
                    self.chars[i] = random.choice(SETTINGS['BACKGROUND_CHARS'])
                    self.intensities[i] = random.randint(1, SETTINGS['BACKGROUND_INTENSITY_LEVELS'])

            # Reset column if it's fully off-screen
            if self.top >= self.height:
                self.top = -self.length
                self._initialize_column()

    def get_column(self):
        visible_length = min(self.length, self.height - self.top)
        column = []
        for i in range(self.height):
            if 0 <= i - self.top < visible_length:
                char = self.chars[i - self.top]
                intensity = self.intensities[i - self.top]
                # Lead character is at the bottom, but not if it's at the very bottom of the screen
                is_lead = (i - self.top == visible_length - 1) and (i < self.height - 1)
            else:
                char = ' '
                intensity = 1
                is_lead = False
            column.append((char, intensity, is_lead))
        return column

class CryptoDisplay:
    def __init__(self, crypto, x, max_y):
        self.crypto = crypto
        self.x = x
        self.y = 0
        self.max_y = max_y
        self.speed = random.uniform(*SETTINGS['CRYPTO_FALL_SPEED_RANGE'])
        self.counter = 0

    def update(self, dt):
        self.counter += dt
        if self.counter >= self.speed:
            self.counter = 0
            self.y += 1

    def is_offscreen(self):
        return self.y > self.max_y + len(self.get_display_text())

    def get_display_text(self):
        return f"{self.crypto['ticker']} ${self.crypto.get('price', 'N/A')}".upper()  # the space after $ allows for a gap between $ and price number

def safe_addstr(stdscr, y, x, text, attr):
    try:
        stdscr.addstr(int(y), x, text, attr)
    except curses.error:
        pass

def main(stdscr):
    config = load_cryptos(config_filename)
    crypto_list = config['cryptos']

    # Use command-line argument for crypto color if provided, otherwise use SETTINGS
    crypto_color = args.crypto_color if args.crypto_color else SETTINGS['CRYPTO_COLOR']
    init_color_pairs(args.bg_color, crypto_color)

    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)   # Make getch() non-blocking

    max_y, max_x = stdscr.getmaxyx()
    
    # Create matrix columns based on the background pattern
    matrix_columns = []
    x = 0
    while x < max_x:
        for gap in SETTINGS['BACKGROUND_PATTERN']:
            if x < max_x:
                matrix_columns.append(MatrixColumn(max_y))
                x += 1
            x += gap

    crypto_displays = []

    threading.Thread(target=update_prices_periodically, args=(crypto_list, config_filename, 75), daemon=True).start()

    try:
        last_time = time.time()
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            stdscr.erase()

            # Update and draw matrix background
            x = 0
            for column in matrix_columns:
                column.update(dt)
                for y, (char, intensity, is_lead) in enumerate(column.get_column()):
                    if char != ' ':  # Don't draw spaces
                        if is_lead:
                            attr = curses.color_pair(9) | curses.A_BOLD
                        else:
                            fade_length = SETTINGS['FADE_LENGTH']
                            if fade_length > 0:
                                if y < fade_length:
                                    color = curses.color_pair(min(8, 2 + y))
                                elif y > max_y - fade_length:
                                    color = curses.color_pair(min(8, 2 + (max_y - y)))
                                else:
                                    color = curses.color_pair(1)
                                attr = color | curses.A_DIM * intensity
                            else:
                                attr = curses.color_pair(1) | curses.A_DIM * intensity
                        safe_addstr(stdscr, y, x, char, attr)
                x += 1
                for _ in range(SETTINGS['BACKGROUND_PATTERN'][x % len(SETTINGS['BACKGROUND_PATTERN'])]):
                    x += 1

            # Update and draw crypto displays
            for display in crypto_displays[:]:
                display.update(dt)
                if display.is_offscreen():
                    crypto_displays.remove(display)
                else:
                    text = display.get_display_text()
                    for i, char in enumerate(text):
                        y = display.y + i
                        if 0 <= y < max_y:
                            fade_length = SETTINGS['FADE_LENGTH']
                            if fade_length > 0:
                                if y < fade_length:
                                    color = curses.color_pair(min(8, 2 + y))
                                elif y > max_y - fade_length:
                                    color = curses.color_pair(min(8, 2 + (max_y - y)))
                                else:
                                    color = curses.color_pair(10)
                                attr = color | curses.A_BOLD
                            else:
                                attr = curses.color_pair(10) | curses.A_BOLD
                            safe_addstr(stdscr, y, display.x, char, attr)

            # Add new crypto display if needed
            if len(crypto_displays) < SETTINGS['CRYPTO_DISPLAY_COUNT'] and random.random() < SETTINGS['CRYPTO_DISPLAY_CHANCE']:
                new_crypto = random.choice(crypto_list)
                new_display = CryptoDisplay(new_crypto, random.randint(0, max_x - 1), max_y)
                crypto_displays.append(new_display)

            stdscr.refresh()

            # Check for user input
            if stdscr.getch() != -1:
                break

            time.sleep(SETTINGS['ANIMATION_SPEED'])

    except KeyboardInterrupt:
        logger.info('Graceful shutdown initiated by user.')
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        curses.curs_set(1)  # Show the cursor again
        print("\nSuccessfully Closed. You can also use matrix_crypto.py --help to see all options")

if __name__ == '__main__':
    curses.wrapper(main)
