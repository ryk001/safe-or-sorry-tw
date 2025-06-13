from main import get_travel_advisory, send_telegram_message, generate_message
import asyncio
import os
import sys
import json
from pathlib import Path
import datetime as dt
from config import TOKEN, CHANNEL

STATUS_FILE = Path('data/last_level.json')

def get_last_level():
    try:
        return json.load(STATUS_FILE.open())['last_level']
    except:
        return None

def save_level(level):
    try:
        json.dump({'last_level': level, 'last_update': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}, STATUS_FILE.open('w'), indent=2)
    except Exception as e:
        print(f"Error saving level: {str(e)}", file=sys.stderr)

async def check_and_notify():
    travel_adv = get_travel_advisory()
    current_level = travel_adv['level_num']
    last_level = get_last_level()
    
    if current_level != 1 and last_level != current_level:
        levels_map = {
            2: '🔥🔥 警戒變化！建議提高警覺！',
            3: '🔥🔥🔥 警戒變化！立即採取應對措施！！！',
            4: '🔥🔥🔥🔥 警戒變化！立即採取應對措施！！！！',
        }
        message = generate_message(travel_adv, levels_map)
        await send_telegram_message(TOKEN, CHANNEL, message)
        save_level(current_level)
    else:
        print(f"No change in level: {current_level}")

async def main():
    try:
        await check_and_notify()
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
