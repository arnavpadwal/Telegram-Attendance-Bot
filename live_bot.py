import csv
import json
import os.path
from datetime import datetime
from telethon import TelegramClient, events
import sys
from os import system as command

# Loading credentials
with open('/home/arnav/Work/Programs/credentials.json', 'r') as f:
    data = json.load(f)
    group_id = int(
        data['apps']['telegram-tmrt-attendance-tracker']['group_id'])
    api_id = int(data['apps']['telegram-tmrt-attendance-tracker']['api_id'])
    api_hash = data['apps']['telegram-tmrt-attendance-tracker']['api_hash']

client = TelegramClient('session_name', api_id, api_hash)

file_exists = os.path.isfile('attendance.csv')
# Check the OS and create the file accordingly
if file_exists == False and sys.platform.startswith('win'):  # For Windows
    command('type nul > {}'.format('attendance.csv'))
elif file_exists == False:  # For Unix-based systems (Linux, macOS)
    command('touch {}'.format('attendance.csv'))


def save_attendance(data):
    with open('attendance.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Date', 'Name', 'Login Time', 'Logout Time'])
        writer.writerow(data)


@client.on(events.NewMessage(chats=group_id))
async def handle_message(event):
    msg = event.message
    user_id = msg.from_id.user_id
    sender = await event.get_sender()
    if sender.last_name:
        username = f"{sender.first_name} {sender.last_name}"
    else:
        username = f"{sender.first_name}"
    text = msg.message.lower()
    date = event.date.strftime('%d-%m-%Y')
    time = event.date.strftime('%H:%M:%S')
    if text == 'login' or text == 'logout':
        # Check if the user has already logged in/out for today
        with open('attendance.csv', 'r') as file:
            reader = csv.reader(file)
            lines = list(reader)
            today_records = [line for line in lines if line[0]
                             == date and line[1] == username]
            if text == 'login' and not today_records:
                save_attendance([date, username, time, ''])
                await event.reply(f'[BOT] {text.capitalize()} Recorded')
            elif text == 'logout' and today_records:
                # Update the last login record with logout time
                for line in reversed(lines):
                    if line[0] == date and line[1] == username:
                        line[3] = time
                        break
                # Rewrite the entire file with updated data
                with open('attendance.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(lines)
                await event.reply(f'[BOT] {text.capitalize()} Recorded')
        # await client.send_message(user_id, f'[BOT] {text.capitalize()} Recorded')


client.start()
client.run_until_disconnected()
