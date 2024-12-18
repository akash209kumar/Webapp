# contact.py

import pandas as pd

def escape_markdown_v2(text):
    escape_chars = r"\_*[]()~`>#+-=|{}.!<>"
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

def get_contact_links(df, roll_number):
    """
    Retrieves WhatsApp and Telegram links for a given roll number from the DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing student data.
        roll_number (str): Roll number of the student.
    
    Returns:
        str: Formatted message with WhatsApp and Telegram hyperlinks.
    """
    student_data = df[df['roll'] == roll_number]
    
    if student_data.empty:
        return "Roll number not found."
    
    student_row = student_data.iloc[0]
    whatsapp_link = student_row.get('whatsapp', None)
    telegram_link = student_row.get('telegram', None)

    parts = []
    
    if pd.notna(whatsapp_link):
        parts.append(f"[WhatsApp](\\{whatsapp_link})")
    else:
        parts.append(" ")

    if pd.notna(telegram_link):
        parts.append(f"[Telegram](\\{telegram_link})")
    else:
        parts.append(" ")

    # Escape the vertical bar
    separator = " | "

    return separator.join(parts)