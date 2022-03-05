import argparse
import asyncio
import json
import sys

from os import path
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from telegram_ban import report_channels
from dotenv import load_dotenv

load_dotenv()


async def main(args):
    filename_creds = "../../app_creds.json"
    creds = {}
    if path.exists(filename_creds):
        with open(filename_creds, 'r') as f:
            creds = json.loads(f.read())
    if args.api_id and args.api_hash:
        creds["api_id"] = args.api_id
        creds["api_hash"] = args.api_hash

    if "session" not in creds:
        creds["session"] = ""

    with open(filename_creds, 'w') as f:
        f.write(json.dumps(creds))

    client = TelegramClient(StringSession(creds["session"]), creds["api_id"], creds["api_hash"])
    try:
        await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                phone = input("Please, enter your telephone number: ")
                response = await client.send_code_request(phone=phone)
                try:
                    await client.sign_in(phone=phone,
                                         code=input("Please, enter code confirmation: "),
                                         phone_code_hash=response.phone_code_hash)
                except SessionPasswordNeededError:
                    print(f"You have Two Factor Authorization enabled, password is required !!")
                    await client.sign_in(password=input("Please, enter password confirmation: "))
            creds["session"] = client.session.save()
            with open(filename_creds, 'w') as f:
                f.write(json.dumps(creds))
            await report_channels(client)
    except Exception as ex:
        print(f"ex is {ex}", file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--api_id',
                        type=int,
                        help='App api_id from \'API development tools\'')
    parser.add_argument('--api_hash',
                        type=str,
                        help='App api_hash from \'API development tools\'')
    return parser.parse_args()


if __name__ == '__main__':
    asyncio.run(main(parse_args()))
