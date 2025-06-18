from main import get_travel_advisory, send_telegram_message, generate_travel_advisory_message, TOKEN, CHANNEL
import asyncio

async def main():
    travel_adv = get_travel_advisory()
    message = generate_travel_advisory_message(travel_adv)
    await send_telegram_message(TOKEN, CHANNEL, message)

if __name__ == "__main__":
    asyncio.run(main())