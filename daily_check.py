from main import get_travel_advisory, send_telegram_message, generate_message
import asyncio
import os
import sys
import datetime as dt

from config import TOKEN, CHANNEL

async def main():
    travel_adv = get_travel_advisory()
    message = generate_message(travel_adv)
    await send_telegram_message(TOKEN, CHANNEL, message)

if __name__ == "__main__":
    asyncio.run(main())