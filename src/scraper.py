import os
import json
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from logger import logger
from channels import CHANNELS

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

client = TelegramClient("telegram_session", API_ID, API_HASH)


async def main():
    await client.start(phone=PHONE_NUMBER)

    me = await client.get_me()
    print(f"Connected as: {me.first_name}")
    logger.info(f"Connected as {me.first_name}")

    print("\nChecking channels...\n")

    # Create base folder (data lake structure)
    date_folder = datetime.now().date()
    base_folder = f"data/raw/telegram_messages/{date_folder}"
    os.makedirs(base_folder, exist_ok=True)

    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)

            print(f"\nChannel found: {entity.title}")
            logger.info(f"Found channel: {entity.title}")

            messages = []

            print(f"Scraping messages from {entity.title}...")

            # 🔥 SCRAPING STARTS HERE
            async for message in client.iter_messages(entity, limit=200):

                # =========================
                # IMAGE DOWNLOAD (FIXED)
                # =========================
                image_path = None

                if message.media:
                    image_folder = f"data/raw/images/{channel}"
                    os.makedirs(image_folder, exist_ok=True)

                    image_path = f"{image_folder}/{message.id}.jpg"

                    try:
                        await message.download_media(file=image_path)
                    except Exception as e:
                        logger.error(f"Image download failed for {message.id}: {e}")
                        image_path = None

                # =========================
                # BUILD MESSAGE RECORD
                # =========================
                data = {
                    "message_id": message.id,
                    "channel_name": channel,
                    "message_date": str(message.date),
                    "message_text": message.message,
                    "views": message.views,
                    "forwards": message.forwards,
                    "has_media": True if message.media else False,
                    "image_path": image_path
                }

                messages.append(data)

            # =========================
            # SAVE TO DATA LAKE
            # =========================
            file_path = f"{base_folder}/{channel}.json"

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=4)

            print(f"Saved {len(messages)} messages → {file_path}")
            logger.info(f"Saved {len(messages)} messages for {channel}")

        except Exception as e:
            print(f"Cannot access {channel}: {e}")
            logger.error(f"Cannot access {channel}: {e}")


with client:
    client.loop.run_until_complete(main())

# import os
# from dotenv import load_dotenv
# from telethon import TelegramClient
# from logger import logger
# from channels import CHANNELS

# # Load environment variables
# load_dotenv()

# API_ID = int(os.getenv("API_ID"))
# API_HASH = os.getenv("API_HASH")
# PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# client = TelegramClient("telegram_session", API_ID, API_HASH)


# async def main():
#     await client.start(phone=PHONE_NUMBER)

#     me = await client.get_me()

#     print(f"Connected as: {me.first_name}")
#     logger.info(f"Connected as {me.first_name}")

#     print("\nChecking channels...\n")

#     for channel in CHANNELS:
#         try:
#             entity = await client.get_entity(channel)

#             print(f"Channel found: {entity.title}")
#             logger.info(f"Found channel: {entity.title}")

#         except Exception as e:
#             print(f"Cannot access {channel}: {e}")
#             logger.error(f"Cannot access {channel}: {e}")


# with client:
#     client.loop.run_until_complete(main())