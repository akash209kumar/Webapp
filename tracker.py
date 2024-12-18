import pandas as pd
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Path to the user log Excel file
user_log_file = 'user_log.xlsx'

# User IDs allowed to access the announcement
ADMIN_USER_IDS = {6986667023, 6220013615}  # Replace with actual admin user IDs

# Path to the user log Excel file
user_log_file = 'user_log.xlsx'

def log_user_command(username: str, user_id: int, user_command: str):
    """Log user commands in an Excel file."""
    try:
        # Check if the log file exists
        if os.path.exists(user_log_file):
            df = pd.read_excel(user_log_file)
        else:
            # Create a new DataFrame if the log file does not exist
            df = pd.DataFrame(columns=['User ID', 'Username', 'Commands'])

        # Update existing log or append a new entry
        if user_id in df['User ID'].values:
            # Get the row index for the user
            user_index = df.index[df['User ID'] == user_id].tolist()[0]
            # Append new command
            current_commands = df.at[user_index, 'Commands']
            if pd.isna(current_commands):
                current_commands = ""
            df.at[user_index, 'Commands'] = f"{current_commands}, {user_command}".strip(", ")
        else:
            # Append new entry for a new user
            new_data = pd.DataFrame([[user_id, username, user_command]], columns=['User ID', 'Username', 'Commands'])
            df = pd.concat([df, new_data], ignore_index=True)

        # Write the updated DataFrame back to the Excel file
        df.to_excel(user_log_file, index=False, engine='openpyxl')  # Specify engine
        print(f"Logged command for user: {username}, command: {user_command}")  # Debug print
    except Exception as e:
        print(f"Failed to log command for {username}: {e}")  # Capture and print the error

def get_user_list():
    """Return the DataFrame of logged user data."""
    if os.path.exists(user_log_file):
        return pd.read_excel(user_log_file)
    return None

def is_authorized(user_id: int) -> bool:
    """Check if a user is authorized to access the command."""
    return user_id in ADMIN_USER_IDS

def announce_bot_online(update: Update, context: CallbackContext):
    """Send an announcement message to all users that the bot is online."""
    user_list = get_user_list()
    if user_list is not None:
        for index, row in user_list.iterrows():
            user_id = row['User ID']
            username = row['Username']
            try:
                # Send the announcement message
                context.bot.send_message(chat_id=user_id, text="🚀 The bot is now online! Hello, {}".format(username))
            except Exception as e:
                print(f"Could not send message to {user_id}: {e}")

def start(update: Update, context: CallbackContext):
    """Send a welcome message when the command /start is issued."""
    update.message.reply_text('Hello! I am your bot.')
    log_user_command(update.message.from_user.username or "N/A", update.message.from_user.id, '/start')

def handle_message(update: Update, context: CallbackContext):
    """Handle regular messages and log them."""
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "N/A"
    user_command = update.message.text.strip()  # User input text
    
    log_user_command(username, user_id, user_command)

def main():
    # Your bot's token
    TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # Replace with your actual Telegram bot token
    
    # Create the Updater and pass it your bot's token
    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("announce_online", announce_bot_online))

    # Message handler for logging user messages
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the updater
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
