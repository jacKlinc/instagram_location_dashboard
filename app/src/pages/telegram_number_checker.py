import streamlit as st
import pandas as pd
import httpx
import asyncio
import json
import os
import re
from getpass import getpass

from dotenv import load_dotenv
from telethon.sync import TelegramClient, errors, functions
from telethon.tl import types


from ..types import Page, TelegramResponse

load_dotenv()


class TelegramNumberChecker(Page):
    API_ID: int  # TODO regex type check
    API_HASH: str  # TODO regex type check
    PHONE_NUMBER: str  # TODO regex type check

    client: TelegramClient

    def write(self):
        self.sidebar()
        st.title("Telegram Phone Number Checker")
        st.text(
            "This section will use the existing Bellingcat repo to search for activity in an area"
        )
        phone_numbers = st.text_input(
            "Please enter the phone numbers you want to check"
        )
        if st.button("Get Results") and phone_numbers != "":
            asyncio.run(self.run_program(phone_numbers))

    def sidebar(self):
        st.sidebar.markdown("### Your Telegram Details")

        # TODO: add regex to for check correct format
        api_id_str = st.sidebar.text_input(
            "Please enter your Telegram API_ID", type="password"
        )
        if api_id_str:
            self.API_ID = int(api_id_str)
        self.API_HASH = st.sidebar.text_input(
            "Please enter your Telegram API_HASH", type="password"
        )
        self.PHONE_NUMBER = st.sidebar.text_input("Please enter your Phone Number")

    async def login(self):
        """Create a telethon session or reuse existing one"""
        client = TelegramClient(self.PHONE_NUMBER, self.API_ID, self.API_HASH)
        client.start()

        # async def main():
        #     # Now you can use all client methods listed below, like for example...
        #     await client.send_message('me', 'Hello to myself!')

        # async with client:
        #     client.loop.run_until_complete(main())

        # try:
        #     await client.connect()
        # except Exception as e:
        #     print(e)
        #     with st.popover("Enter the code (sent on telegram)"):
        #         self.telegram_mfa = st.text_input("MFA Code", type="password")
        #     await client.connect()
        # client.start()

        # await client.connect()
        # if not await client.is_user_authorized():
        #     await client.send_code_request(self.PHONE_NUMBER)
        #     try:
        #         print(self.PHONE_NUMBER, self.telegram_mfa)
        #         await client.sign_in(self.PHONE_NUMBER, self.telegram_mfa)
        #     except errors.SessionPasswordNeededError:
        #         with st.popover("Enter the code (sent on telegram)"):
        #             self.telegram_mfa = st.text_input("MFA Code", type="password")
        #         await client.sign_in(password=self.telegram_mfa)
        # self.client = client

    async def validate_users(self, phone_numbers: str) -> dict[str, types.User]:
        """
        Take in a string of comma separated phone numbers and try to get the user information associated with each phone number.
        """
        result = {}
        phones = [
            re.sub(r"\s+", "", p, flags=re.UNICODE) for p in phone_numbers.split(",")
        ]
        try:
            for phone in phones:
                if phone not in result:
                    result[phone] = await self.get_names(phone)
        except Exception as e:
            print(e)
            raise
        return result

    async def run_program(self, phone_numbers: str):
        await self.login()
        # res = await self.validate_users(phone_numbers)
        # df = pd.DataFrame(res).transpose()
        # st.write(df)
        # st.write(res)
        # self.client.disconnect()

    def get_human_readable_user_status(self, status: types.TypeUserStatus):
        match status:
            case types.UserStatusOnline():
                return "Currently online"
            case types.UserStatusOffline():
                return status.was_online.strftime("%Y-%m-%d %H:%M:%S %Z")
            case types.UserStatusRecently():
                return "Last seen recently"
            case types.UserStatusLastWeek():
                return "Last seen last week"
            case types.UserStatusLastMonth():
                return "Last seen last month"
            case _:
                return "Unknown"

    async def get_names(self, phone_number: str) -> dict[str, types.User]:
        """Take in a phone number and returns the associated user information if the user exists.

        It does so by first adding the user's phones to the contact list, retrieving the
        information, and then deleting the user from the contact list.
        """
        result = {}
        try:
            # Create a contact
            contact = types.InputPhoneContact(
                client_id=0, phone=phone_number, first_name="", last_name=""
            )
            # Attempt to add the contact from the address book
            contacts = await self.client(
                functions.contacts.ImportContactsRequest([contact])
            )

            users = contacts.to_dict().get("users", [])
            number_of_matches = len(users)

            if number_of_matches == 0:
                result.update(
                    {
                        "error": "No response, the phone number is not on Telegram or has blocked contact adding."
                    }
                )
            elif number_of_matches == 1:
                # Attempt to remove the contact from the address book.
                # The response from DeleteContactsRequest contains more information than from ImportContactsRequest
                updates_response: types.Updates = await self.client(
                    functions.contacts.DeleteContactsRequest(id=[users[0].get("id")])
                )
                user = updates_response.users[0]
                # getting more information about the user
                result.update(
                    {
                        "id": user.id,
                        "username": user.username,
                        "usernames": user.usernames,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "fake": user.fake,
                        "verified": user.verified,
                        "premium": user.premium,
                        "mutual_contact": user.mutual_contact,
                        "bot": user.bot,
                        "bot_chat_history": user.bot_chat_history,
                        "restricted": user.restricted,
                        "restriction_reason": user.restriction_reason,
                        "user_was_online": get_human_readable_user_status(user.status),
                        "phone": user.phone,
                    }
                )
            else:
                result.update(
                    {
                        "error": """This phone number matched multiple Telegram accounts, 
                which is unexpected. Please contact the developer: contact-tech@bellingcat.com"""
                    }
                )

        except TypeError as e:
            result.update(
                {
                    "error": f"TypeError: {e}. --> The error might have occurred due to the inability to delete the {phone_number=} from the contact list."
                }
            )
        except Exception as e:
            result.update({"error": f"Unexpected error: {e}."})
            raise
        return result
