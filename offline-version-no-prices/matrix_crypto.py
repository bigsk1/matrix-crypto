import json
import curses
import time
import random
import argparse
import logging


# Setup logging
logging.basicConfig(filename='matrix_crypto.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Matrix-style crypto ticker display.")
parser.add_argument('-s', '--speed', type=int, default=250, help='Speed of the falling text, higher is slower.')
parser.add_argument('--color', type=str, help='Color of the falling text (green, red, blue, etc.). Default is specified in config.json or green if not specified.')
args = parser.parse_args()

# Load crypto configuration data from a JSON file
def load_cryptos(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.error(f'Failed to load configuration: {e}')
        exit(1)

def init_color_pair(color_name, default_color='green'):
    color_map = {
        'red': curses.COLOR_RED,
        'green': curses.COLOR_GREEN,
        'blue': curses.COLOR_BLUE,
        'yellow': curses.COLOR_YELLOW,
        'cyan': curses.COLOR_CYAN,
        'magenta': curses.COLOR_MAGENTA,
        'white': curses.COLOR_WHITE,
    }
    chosen_color = color_map.get(color_name, color_map[default_color])
    curses.start_color()
    curses.init_pair(1, chosen_color, curses.COLOR_BLACK)

def main(stdscr):
    config = load_cryptos('cryptos_config.json')
    color = args.color if args.color else config.get('color', 'green')
    init_color_pair(color)

    crypto_list = config.get('cryptos', [])
    
    max_y, max_x = stdscr.getmaxyx()
    num_columns = len(crypto_list)
    positions = [random.randint(-max_y, 0) for _ in range(num_columns)]

    try:
        while True:
            stdscr.clear()
            for i, crypto in enumerate(crypto_list):
                string = f"{crypto['ticker']}"
                pos = positions[i]
                for j, char in enumerate(string):
                    y_pos = (pos + j) % (max_y + len(string))
                    if 0 <= y_pos < max_y:
                        x_pos = (i * max_x // num_columns)
                        try:
                            stdscr.addstr(y_pos, x_pos, char, curses.color_pair(1))
                        except curses.error:
                            pass
                positions[i] += random.randint(1, 2)
            stdscr.refresh()
            time.sleep(max(0.01, args.speed / 1000.0))
    except KeyboardInterrupt:
        logging.info('Graceful shutdown initiated by user.')
        print("\nClosed Successfully. Use matrix_crypto.py --help for more options")
        # Clean up or closing actions go here

if __name__ == '__main__':
    curses.wrapper(main)