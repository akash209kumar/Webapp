import pandas as pd
from telegram import Update
from telegram.ext import ContextTypes
import os

AUTHORIZED_USER_ID = 6986667023

def get_user_ids_from_log(file_path='user_log.xlsx'):
    """Read user IDs from user_log.xlsx and return them as a list."""
    try:
        # Read user IDs from the specified file
        df = pd.read_excel(file_path)
        
        # Getting the list of user IDs from the 'User ID' column
        if 'User ID' in df.columns:
            user_ids = df['User ID'].dropna().astype(str).tolist()
            return [int(uid) for uid in user_ids if uid.isdigit()]  # Convert to integers
        else:
            print("Column 'User ID' not found in user_log.xlsx")
            return []
    except Exception as e:
        print(f"Error reading user IDs from {file_path}: {e}")
        return []

async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check if user is authorized to make announcements
    if user_id != AUTHORIZED_USER_ID:
        await update.message.reply_text("You are not authorized to make announcements.")
        return

    # Join all arguments after the command as the announcement message
    announcement_message = ' '.join(context.args)

    if not announcement_message:
        await update.message.reply_text("Please provide a message to announce.")
        return

    # Get user IDs from user_log.xlsx
    user_ids = get_user_ids_from_log('user_log.xlsx')  # Adjust the path if necessary

    if not user_ids:
        await update.message.reply_text("No user IDs found for announcements.")
        return

    success_count = 0
    failure_count = 0

    # Iterate through user IDs and send the announcement
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=announcement_message)
            success_count += 1
        except Exception as e:
            print(f"Could not send message to {uid}: {e}")
            failure_count += 1

    success_msg = f"Announcement sent successfully to {success_count} user(s)."
    
    if failure_count > 0:
        success_msg += f" {failure_count} user(s) could not be contacted."

    await update.message.reply_text(success_msg)
