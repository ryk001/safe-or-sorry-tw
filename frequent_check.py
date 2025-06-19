from main import (
    get_travel_advisory,
    send_telegram_message,
    generate_travel_advisory_message,
    get_ait_alert,
    generate_ait_alert_message,
    TOKEN,
    CHANNEL
)
from pathlib import Path
import datetime as dt
import asyncio
import json
import sys
import os

STATUS_FILE = Path('data/last_level.json')
AIT_HISTORY_FILE = Path('data/ait_alert_history.json')

def load_last_level():
    try:
        return json.load(STATUS_FILE.open())['last_level']
    except:
        return None

def save_level(level):
    try:
        json.dump({'last_level': level, 'last_update': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}, STATUS_FILE.open('w'), indent=2)
    except Exception as e:
        print(f"Error saving level: {str(e)}", file=sys.stderr)

def load_ait_alert_history():
    if not AIT_HISTORY_FILE.exists():
        AIT_HISTORY_FILE.parent.mkdir(exist_ok=True)
        with open(AIT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({'last_update': None, 'alerts': []}, f, ensure_ascii=False, indent=2)
        return {'last_update': None, 'alerts': []}
    with open(AIT_HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_ait_alert_history(history):
    history['last_update'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    with open(AIT_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

async def check_travel_advisory():
    travel_adv = get_travel_advisory()
    current_level = travel_adv['level_num']
    last_level = load_last_level()
    if current_level != 1 and last_level != current_level:
        levels_map = {
            2: '🟡🟡 警示等級變化！建議提高警覺！',
            3: '🟠🟠🟠 警示等級變化！立即採取應對措施！！！',
            4: '🔴🔴🔴🔴 警示等級變化！立即採取應對措施！！！！',
        }
        message = generate_travel_advisory_message(travel_adv, levels_map)
        await send_telegram_message(TOKEN, CHANNEL, message)
        save_level(current_level)
    else:
        print(f"No change in level: {current_level}")

async def check_ait_alerts():
    history = load_ait_alert_history()
    alert_history = history['alerts']
    current_alerts = get_ait_alert()
    new_alerts = []
    for alert in current_alerts:
        if alert['link'] not in alert_history:
            new_alerts.append(alert)
            alert_history.append(alert['link'])
    if new_alerts:
        for alert in new_alerts:
            message = generate_ait_alert_message(alert)
            await send_telegram_message(TOKEN, CHANNEL, message)
        history['alerts'] = alert_history
        save_ait_alert_history(history)
        print(f"Found and saved {len(new_alerts)} new AIT alerts")
    else:
        print("No new alerts found")

async def main():
    try:
        await check_travel_advisory()
        await check_ait_alerts()
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
