from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import subprocess
import os
from telegram import Bot

# Replace 'YOUR_BOT_TOKEN' with the token provided by BotFather
TOKEN = os.environ['TOKEN']

# Specify the allowed chat IDs of the desired group of users
ALLOWED_CHAT_IDS = os.environ['ALLOWED_CHAT_IDS']  # Add the desired chat IDs here

def start(update, context):
    if update.message.chat_id not in ALLOWED_CHAT_IDS:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Sorry, you are not authorized to use this bot.')
        return

def process_file(update, context):
    # Check if the message is from an allowed chat ID
    if update.message.chat_id not in ALLOWED_CHAT_IDS:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Sorry, you are not authorized to use this bot.')
        return

    document = update.message.document
    file = context.bot.get_file(document.file_id)
    file_path = file.download()

    # Rename the downloaded file to data.json
    new_file_path = os.path.join(os.path.dirname(file_path), 'data.json')
    os.rename(file_path, new_file_path)

    # Run the scripts locally
    run_script('parse_json.py')
    run_script('scanner_ip.py')

    # Read the content from result1.txt
    result_path = os.path.join(os.path.dirname(__file__), 'result1.txt')
    with open(result_path, 'r') as result_file:
        result_content = result_file.read()

    # Send the content back to the user
    context.bot.send_message(chat_id=os.environ['CHAT_ID'], text=result_content)

    # Clean up the files
    clean_files()

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    subprocess.run(['python', script_path])

def clean_files():
    # Clean up data.json and result1.txt files
    json_file_path = os.path.join(os.path.dirname(__file__), 'data.json')
    txt_file_path1 = os.path.join(os.path.dirname(__file__), 'result.txt')
    txt_file_path2 = os.path.join(os.path.dirname(__file__), 'result1.txt')

    if os.path.exists(json_file_path):
        os.remove(json_file_path)
    if os.path.exists(txt_file_path1):
        os.remove(txt_file_path1)
    if os.path.exists(txt_file_path2):
        os.remove(txt_file_path2)

def main():
    clean_files()
    bot = Bot(token=TOKEN)
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    file_handler = MessageHandler(Filters.document, process_file)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(file_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
