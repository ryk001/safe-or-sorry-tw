from bs4 import BeautifulSoup
from telegram import Bot
import requests
import re
import datetime as dt
import asyncio
import os
import sys
# Telegram Configuration
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHANNEL = '@safeorsorrytw' # '6677853526'

def get_travel_advisory(country="taiwan"):
    country = country.lower().replace(' ', '-')
    url = f"https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/{country}-travel-advisory.html"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        text = soup.get_text()
        level = re.search(rf'{country.title().replace("-", " ")} - (Level \d+: [^\n]+)', text).group(1)
        
        alert = soup.find('div', class_='tsg-rwd-emergency-alert-text')
        description = alert.find_all('p')[1].get_text(strip=True) if (alert and len(alert.find_all('p')) > 1) else 'No reason found'

        reasons = {
            i.get_text(strip=True, separator=' ') : i.get('data-tooltip').replace('\xa0', ' ').strip() \
            for i in soup.find_all(class_='showThreat')
        }
            
        return {'country': country.title(), 'level_num': int(level.split(':')[0].split(' ')[1]), 'level_text': level, 'description': description, 'reasons': reasons}
        
    except requests.RequestException as e:
        return {"error": f"Error fetching data: {str(e)}"}

def generate_message(travel_adv:dict, levels_map=None):
    
    current_time = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    weekday_phrase = '乖乖去上班吧' if current_time.weekday() < 5 else '好好享受假日吧'
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    levels_map = {
        1: f'今天很安全，{weekday_phrase}。',
        2: '🚨🚨 警戒升級！建議提高警覺！',
        3: '🚨🚨🚨 非常危險！請立即採取應對措施！！！',
        4: '🚨🚨🚨🚨 極度危險！請立即採取應對措施！！！',
    } if levels_map is None else levels_map
    reasons_map = {
        "C": "犯罪率",
        "T": "恐怖主義活動",
        "U": "社會動盪",
        "N": "天災",
        "H": "衛生健康問題",
        "K": "綁架或扣押人質",
        "D": "不正當拘留",
        "O": "其他",
    }
    message = f"{levels_map[travel_adv['level_num']]}\n\n"
    if travel_adv['reasons']!={}:
        message += f"警戒原因：{'、'.join(reasons_map[k] for k in sorted(travel_adv['reasons'].keys()))}。\n\n"
    message += f"原始訊息: \n{travel_adv['country']} - {travel_adv['level_text']}\n"
    if travel_adv['reasons']!={}:
        message += '\n'
        for k, v in travel_adv['reasons'].items():
            message += f"{k}: {v}\n"
    message += f"\n{travel_adv['description']}\n\n"
    message += f"更新時間: {current_time}"

    return message

async def send_telegram_message(token, channel, text):
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=channel, text=text)
    except Exception as e:
        print(f"Error sending telegram message: {str(e)}", file=sys.stderr)
        sys.exit(1)