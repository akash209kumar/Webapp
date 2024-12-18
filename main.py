import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import pytz
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)
from io import BytesIO
import os
import logging
import httpx
import asyncio

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
httpx_log = logging.getLogger("httpx")
httpx_log.setLevel(logging.WARNING)

# Load data from the Excel file for student info
excel_file = 'data.xlsx'
try:
    df = pd.read_excel(excel_file, dtype={
        'roll': str,
        'phone': str,
        'whatsapp': str,
        'telegram': str,
        'name': str,
        'section-6th': str,
        'section-5th': str,
        'hostel': str,
        'kiitmail': str,
        'email': str
    })
except Exception as e:
    logging.error(f"Error reading the Excel file: {e}")
    df = pd.DataFrame()  # Initialize as empty DataFrame if there is an error

# Load user IDs from the Excel files specified
USER_COMMANDS_FILE = 'user_commands.xlsx'
USER_LOG_FILE_PATH = "user_log.xlsx"

def load_user_ids():
    if os.path.exists(USER_COMMANDS_FILE):
        df = pd.read_excel(USER_COMMANDS_FILE)
        return set(df['User ID'].dropna().astype(str).tolist())
    return set()

def load_user_ids_from_log():
    """Load user IDs from user_log.xlsx."""
    if os.path.exists(USER_LOG_FILE_PATH):
        df = pd.read_excel(USER_LOG_FILE_PATH)
        return set(df['User ID'].dropna().astype(str).tolist())
    return set()

def save_user_ids(user_ids):
    df = pd.DataFrame({'User ID': list(user_ids)})
    df.to_excel(USER_COMMANDS_FILE, index=False)

# Store unique user IDs
user_ids = load_user_ids()

# Initialize required constants
AUTHORIZED_USER_ID = 6986667023  # Replace with your actual authorized user ID

# Helper functions
def escape_markdown_v2(text):
    escape_chars = r"\_*[]()~`>#+-=|{}.!<>"
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

def split_message(message, chunk_size=3500):
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

def get_contact_links(df: pd.DataFrame, roll_number: str) -> str:
    student_data = df[df['roll'] == roll_number]

    if student_data.empty:
        return "Roll number not found."

    student_row = student_data.iloc[0]
    whatsapp_link = student_row.get('whatsapp', None)
    telegram_link = student_row.get('telegram', None)

    links = []
    if pd.notna(whatsapp_link):
        links.append(f"[WhatsApp]({whatsapp_link})")
    else:
        links.append(" ")

    if pd.notna(telegram_link):
        links.append(f"[Telegram]({telegram_link})")
    else:
        links.append(" ")

    contact_links_message = " | ".join(links)  # Escape the '|' character
    return contact_links_message

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or "N/A"
    message = "Welcome to ⭕️FINDER__×\n\nTo see my capabilities input your ROLL NO\n\nuse /help to know more commands."

    local_photo_path = "xen.jpg"  # Replace this with your own local image path

    with open(local_photo_path, 'rb') as photo:
        await update.message.reply_photo(photo=photo, caption=message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "⭕️ Send a roll number (e.g., 220517xx)\n"
        "⭕️ Send a section code (e.g., '5' for CSE-5)\n"
        "⭕️ Send a name to get relevant name\n\n"
        "✖️ ✖️✖️✖️✖️✖️✖️✖️✖️ ✖️\n"
        "✖️Developed by: Ankush✖️\n"
        "✖️ ✖️✖️✖️✖️✖️✖️✖️✖️ ✖️\n\n"
        "⭕️Admins only commands\n"
        "/users\n"
        "/announce"
    )
    await update.message.reply_text(help_text)

# List of special roll numbers and their corresponding messages
SPECIAL_ROLL_NUMBERS = {
    "22051748": "Hello There!\nIts me !\n\n🅒🅡🅔🅐🅣🅞🅡  🅞🅕  🅣🅗🅔  🅑🅞🅣 \n\n",
    
}

async def get_data(update: Update, context: ContextTypes.DEFAULT_TYPE, roll_number: str):
    # Check if the roll number is in the list of special ones
    if roll_number in SPECIAL_ROLL_NUMBERS:
        special_message = (
            f"𝑺𝑶𝑽𝑬𝑹𝑬𝑰𝑮𝑵 𝑰𝑫𝑬𝑵𝑻𝑰𝑭𝑰𝑬𝑫\n\n\n"
            f"{SPECIAL_ROLL_NUMBERS[roll_number]}\n"
        )
        await update.message.reply_text(special_message)
        return

    student_data = df[df['roll'] == roll_number]

    if not student_data.empty:
        row = student_data.iloc[0]
        message_parts = []

        # Only add details that are not NaN
        if pd.notna(row.get('name')):
            message_parts.append(f"Name: {row['name']}")
        if pd.notna(row.get('roll')):
            message_parts.append(f"Roll No: {row['roll']}")
        if pd.notna(row.get('section-6th')):
            message_parts.append(f"Section (6th): {row['section-6th']}")
        if pd.notna(row.get('section-5th')):
            message_parts.append(f"Section (5th): {row['section-5th']}")
        if pd.notna(row.get('sec2nd')):
            message_parts.append(f"Section (2nd yr): {row['sec2nd']}")    
        if pd.notna(row.get('phone')):
            message_parts.append(f"Phone: {row['phone']}")
        if pd.notna(row.get('hostel')):
            message_parts.append(f"Hostel: {row['hostel']}")
        if pd.notna(row.get('kiitmail')):
            message_parts.append(f"KIIT Email: {row['kiitmail']}")
        if pd.notna(row.get('email')):
            message_parts.append(f"Email: {row['email']}")

        # Join the message parts with line breaks
        message = "\n\n".join(message_parts)

        # Retrieve and append contact links if they exist
        contact_links = get_contact_links(df, roll_number)
        if contact_links and contact_links.strip():  # Only add if there are actual links available
            message += "\n\n" + contact_links.strip()

        # Send message
        for chunk in split_message(message):
            try:
                await update.message.reply_text(chunk, parse_mode='Markdown', disable_web_page_preview=True)
            except Exception as e:
                logging.error(f"Failed to send message: {chunk}. Error: {e}")
    else:
        await update.message.reply_text("Roll number not found.")



async def get_section(update: Update, context: ContextTypes.DEFAULT_TYPE, section: str):
    # Extract branch and section number#+
    parts = section.upper().split('-')#+
    if len(parts) != 2:#+
        await update.message.reply_text("Invalid format. Please use format like 'CSE-01' or 'IT-01'.")#+
        return#+

    
    branch, section_number = parts#+


    keyboard = [#+
        [#+
            InlineKeyboardButton("2nd Year", callback_data=f"section_2_{branch}_{section_number}"),#+
            InlineKeyboardButton("3rd Year", callback_data=f"section_3_{branch}_{section_number}")#+
        ]#+
    ]#+
    reply_markup = InlineKeyboardMarkup(keyboard)#+
    await update.message.reply_text(f"Please choose the year for {branch}-{section_number.zfill(2)}:", reply_markup=reply_markup)#+
#+
async def button_handler(update: Update, context: CallbackContext):#+
    query = update.callback_query#+
    await query.answer()#+
#+
    data = query.data.split("_")#+
    if data[0] == "section":#+
        year = data[1]#+
        branch = data[2]#+
        section_number = data[3]#+
        await send_section_data(update, context, f"{branch}-{section_number}", year)#+
async def send_section_data(update: Update, context: ContextTypes.DEFAULT_TYPE, section: str, year: str):
    if year == "2":
      
        section_data = df[df['sec2nd'].str.contains(section, na=False)]#+
    else:
       
        section_data = df[df['section-6th'].str.contains(section, na=False)]#+

    if not section_data.empty:
        total_students = len(section_data)
        male_students = section_data['hostel'].str.startswith('KP').sum()
        female_students = section_data['hostel'].str.startswith('QC').sum()
        day_scholars = total_students - male_students - female_students

        section_message = (

            f"TOTAL STUDENTS : {total_students}\n\n"
            f"MALE   ------------ {male_students}\n"
            f"FEMALE   ---------- {female_students}\n"
            f"DAY SCHOLARS  -- {day_scholars}\n"
        )

        keyboard = [
            [
              
                InlineKeyboardButton("Get Full Student List", callback_data=f"full_list_{year}_{section}")#+
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(section_message, reply_markup=reply_markup)#+
    else:
        await update.callback_query.message.reply_text("Section not found.")#+

# Update the button_handler function to handle the full list request#+
async def button_handler(update: Update, context: CallbackContext):#+
    query = update.callback_query#+
    await query.answer()#+


    data = query.data.split("_")#+
    if data[0] == "section":#+
        year = data[1]#+
        branch = data[2]#+
        section_number = data[3]#+
        await send_section_data(update, context, f"{branch}-{section_number}", year)#+
    elif data[0] == "full_list":#+
        year = data[1]#+
        section = "_".join(data[2:])  # Join the rest of the data to get the full section name#+
        await send_full_student_list(update, context, section, year)#+


async def send_full_student_list(update: Update, context: ContextTypes.DEFAULT_TYPE, section: str, year: str):#+
    if year == "2":#+
        section_data = df[df['sec2nd'].str.contains(section, na=False)]#+
    else:#+
        section_data = df[df['section-6th'].str.contains(section, na=False)]#+

    if not section_data.empty:
        message_parts = []
        for _, row in section_data.iterrows():

            details = f"Name: {escape_markdown_v2(row['name'])}\nRoll No: {escape_markdown_v2(row['roll'])}\n"#+
            message_parts.append(details)


        for chunk in split_message("\n\n".join(message_parts)):#+
            try:
                await update.callback_query.message.reply_text(chunk, parse_mode='MarkdownV2')
            except Exception as e:
                logging.error(f"Error sending full student list: {e}")
    else:
        await update.callback_query.message.reply_text("No students found in this section.")



async def get_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    name = ' '.join(name.split()).strip().lower()
    name_data = df[df['name'].str.contains(name, case=False, na=False)]

    if not name_data.empty:
        message_parts = []
        for _, row in name_data.iterrows():
            escaped_name = escape_markdown_v2(row['name'] if pd.notna(row['name']) else '')
            escaped_roll = escape_markdown_v2(row['roll'] if pd.notna(row['roll']) else '')
            escaped_section = escape_markdown_v2(row['section-6th'] if pd.notna(row['section-6th']) else '')
            hostel = row['hostel']
            hostel_info = "Day Scholar" if pd.isna(hostel) or not hostel.startswith(('KP', 'QC')) else hostel

            message_parts.append(
                f"Name: {escaped_name}\n"
                f"Roll No: {escaped_roll}\n"
                f"Section: {escaped_section}\n"
                f"Hostel: {escape_markdown_v2(hostel_info)}\n\n"
            )

        message = "".join(message_parts)
        for chunk in split_message(message):
            try:
                await update.message.reply_text(chunk, parse_mode='MarkdownV2')
            except Exception as e:
                logging.error(f"Error sending message by name: {e}")
    else:
        await update.message.reply_text("No students found with this name.")


async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    log_user_command(username, user_id, query)  # Log the command

   
    # Check if the query matches the new section format (e.g., CSE-01)#+
    if '-' in query and len(query.split('-')) == 2:#+
        await get_section(update, context, query)#+
    # Check if the query is a roll number (5-9 digits)#+
    elif query.isdigit() and len(query) in range(5, 10):#+
        await get_data(update, context, query)
    # Check if the query is a section number in the old format (1-2 digits)#+
    elif query.isdigit() and len(query) in range(1, 3):#+
        # Convert old format to new format (assuming CSE as default branch)#+
        new_query = f"CSE-{query.zfill(2)}"#+
        await get_section(update, context, new_query)#+
    # If none of the above, treat it as a name search#+
    else:
        await get_by_name(update, context, query)






def log_user_command(username, user_id, query):
    try:
        # Create an IST timezone object
        ist = pytz.timezone('Asia/Kolkata')

        # Get current timestamp in IST
        timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

        if os.path.exists(USER_LOG_FILE_PATH):
            df = pd.read_excel(USER_LOG_FILE_PATH)
        else:
            df = pd.DataFrame(columns=['User ID', 'Username', 'Commands'])

        # Find the user's index
        user_indices = df.index[df['User ID'] == user_id].tolist()

        if user_indices:
            # User exists, update their record
            user_index = user_indices[0]
            
            # Get current commands
            current_commands = df.at[user_index, 'Commands']

            # If column is empty, initialize it
            if pd.isna(current_commands):
                current_commands = f"{query} [{timestamp}]"
            else:
                # Append new command with timestamp
                current_commands = f"{current_commands}, {query} [{timestamp}]"

            # Update the row
            df.at[user_index, 'Commands'] = current_commands

        else:
            # New user, create a new row
            new_data = pd.DataFrame({
                'User ID': [user_id], 
                'Username': [username], 
                'Commands': [f"{query} [{timestamp}]"]
            })
            df = pd.concat([df, new_data], ignore_index=True)

        # Save to Excel
        df.to_excel(USER_LOG_FILE_PATH, index=False)  

    except Exception as e:
        logging.error(f"Failed to log command for {username}: {e}")



async def users_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if is_authorized(user_id):
        if os.path.exists(USER_LOG_FILE_PATH):
            user_logs_df = pd.read_excel(USER_LOG_FILE_PATH)
            
            with BytesIO() as user_log_file_buffer:
                with pd.ExcelWriter(user_log_file_buffer, engine='openpyxl') as writer:
                    user_logs_df.to_excel(writer, index=False, sheet_name='User Logs')
                
                user_log_file_buffer.seek(0)

                await update.message.reply_document(
                    document=user_log_file_buffer, 
                    filename='user_log.xlsx'
                )
        else:
            await update.message.reply_text("User log file not found.")
    else:
        await update.message.reply_text("You are not authorized to access this command.")




# Announcement to the users
async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("You are not authorized to make announcements.")
        return

    announcement_message = ' '.join(context.args)

    if not announcement_message:
        await update.message.reply_text("Please provide a message to announce.")
        return

    # Loading user is from user_log.xlsx
    user_ids = load_user_ids_from_log()

    if not user_ids:
        await update.message.reply_text("No user IDs found for announcements.")
        return

    logging.info("User IDs to send announcements: %s", user_ids)

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=announcement_message)
        except Exception as e:
            logging.error(f"Could not send message to {uid}: {e}")

def is_authorized(user_id):
    return user_id == AUTHORIZED_USER_ID  # authorization checking

# mirch mashala
def main():
    user_ids = load_user_ids_from_log()  # Load user IDs from user_log.xlsx
    
    application = Application.builder().token("8035259116:AAEGPqGEifZr6Srjw_IjslJggjeyuJsZQRA").build()  # kripiya apna apna Token dale 

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("announce", announce))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

    # Add the callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
