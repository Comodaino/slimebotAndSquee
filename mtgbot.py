#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

import logging
import re
import os
import requests
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

pattern = r'\[([^\]]+)\]'

url = 'https://api.scryfall.com/cards/search?q='

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    matches = re.findall(pattern, update.message.text)
    if matches:
        for substring in matches:
            # Extract the matched substring
            print(f"Found substring: {substring}")
            # Send the GET request
            response = requests.get(url + substring)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Print the response content (assuming JSON response)
                data = response.json()
                first_card = data['data'][0]
    
                card_uri = first_card['scryfall_uri']
                card_name = first_card['name']
                image_uri = first_card['image_uris']['normal']
                # Get image
                image_path = "tmp_image.jpg"
                image_response = requests.get(image_uri)
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                await update.message.reply_photo(image_path, card_name + "\n" + card_uri)

                if os.path.exists(image_path):
                    os.remove(image_path)

            else:
                # Print an error message if the request failed
                print(f"Request failed with status code {response.status_code}")
                await update.message.reply_text("no card found")


def main() -> None:
    


    telegram_token = os.getenv("TELEGRAM_TOKEN")
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_token).build()
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
