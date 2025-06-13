from main import get_travel_advisory, send_telegram_message, generate_message, TOKEN, CHANNEL
import datetime as dt
import asyncio
import os
import sys

async def main():
    travel_adv = get_travel_advisory()
    message = generate_message(travel_adv)
    await send_telegram_message(TOKEN, CHANNEL, message)

if __name__ == "__main__":
    asyncio.run(main())