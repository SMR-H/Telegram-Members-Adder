"""
Telegram Group Adder Script
Author: SMR-H - https://github.com/SMR-H
Description: Automates adding members to Telegram groups, managing contacts, and generating reports.
Disclaimer: Use responsibly and comply with Telegram's terms of service.
"""

BANNER = """
\033[1;36m
███████╗███╗   ███╗██████╗       ██╗  ██╗
██╔════╝████╗ ████║██╔══██╗      ██║  ██║
███████╗██╔████╔██║██████╔╝█████╗███████║
╚════██║██║╚██╔╝██║██╔══██╗╚════╝██╔══██║
███████║██║ ╚═╝ ██║██║  ██║      ██║  ██║
╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝      ╚═╝  ╚═╝
\033[0m
"""
print(BANNER)


import pandas as pd
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest, GetContactsRequest
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantsRequest
from telethon.tl.types import InputPhoneContact, InputUser, ChannelParticipantsSearch
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError, PeerFloodError
import time
import os
import random
import json
from configparser import ConfigParser



class TelegramGroupManager:
    def __init__(self):

        self.config = self._load_config()
        self.phone_numbers = self._load_phone_numbers()
        self.client = TelegramClient('session_name', self.config['api_id'], self.config['api_hash'])
        self.group_entity = None
        self.saved_contacts = None
        self.saved_contact_ids = set()
        self.contact_list = []
        self.matches = []
        self.results_report = []  # To store the results for the Excel report

    def _load_config(self):
        """Load and validate configuration from config.ini file. Create it if missing."""
        config_path = 'config.ini'
        required_keys = ['api_id', 'api_hash', 'phone', 'group', 'excel_file', 'invite_link']
        optional_defaults = {'delay': '5', 'max_retries': '3'}

        # Create config if missing
        if not os.path.exists(config_path):
            print("\033[1;33m🛠 Initial configuration required:\033[0m")
            config = ConfigParser()
            config['Telegram'] = {
                'api_id': input("API ID: "),
                'api_hash': input("API Hash: "),
                'phone': input("Your phone (+1234567890): "),
                'group': input("Group username (@group): "),
                'invite_link': input("Group invite link: "),
                'excel_file': input("Path to Excel file: "),
                **optional_defaults
            }
            with open(config_path, 'w') as f:
                config.write(f)
            print("\033[1;32m✅ Configuration saved!\033[0m")

        # Read and validate config
        config = ConfigParser()
        config.read(config_path)

        if not config.has_section('Telegram'):
            raise ValueError("Missing [Telegram] section in config")

        telegram_config = {k.strip().lower(): v.strip() for k, v in config['Telegram'].items()}

        # Validate required fields
        missing = [key for key in required_keys if key not in telegram_config]
        if missing:
            raise ValueError(f"Missing required keys in config: {', '.join(missing)}")

        # Set defaults for optional fields
        for key, default in optional_defaults.items():
            telegram_config.setdefault(key, default)

        # Type conversions
        try:
            telegram_config['api_id'] = int(telegram_config['api_id'])
            telegram_config['delay'] = int(telegram_config['delay'])
            telegram_config['max_retries'] = int(telegram_config['max_retries'])
        except ValueError as e:
            raise ValueError(f"Invalid config value: {e}")

        # Additional validation
        if not os.path.exists(telegram_config['excel_file']):
            raise FileNotFoundError(f"Excel file not found: {telegram_config['excel_file']}")

        # Load invite messages from the JSON file
        telegram_config['invite_messages'] = self._load_invite_messages()

        return telegram_config

    def _load_invite_messages(self):
        """Load invite messages from the JSON file."""
        messages_path = 'invite_messages.json'
        if not os.path.exists(messages_path):
            raise FileNotFoundError(f"Invite messages file '{messages_path}' not found.")

        with open(messages_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_phone_numbers(self):
        """Load phone numbers from the Excel file."""
        if not os.path.exists(self.config['excel_file']):
            raise FileNotFoundError(f"Excel file '{self.config['excel_file']}' not found.")

        df = pd.read_excel(self.config['excel_file'])
        df.columns = df.columns.str.strip().str.lower()

        if 'phone' not in df.columns:
            raise ValueError("Excel file must contain a 'Phone' column.")

        # Ensure phone numbers start with '+'
        phone_numbers = df['phone'].astype(str).tolist()
        return ['+' + phone if not phone.startswith('+') else phone for phone in phone_numbers]

    def _initialize_client(self):
        """Initialize the Telegram client and fetch necessary entities."""
        self.client.start(phone=self.config['phone'])
        print(50 * '-')
        print("✅ Logged in successfully.")

        # Get existing contacts and group entity
        self.saved_contacts = self.client(GetContactsRequest(hash=0)).users
        self.saved_contact_ids = {user.id for user in self.saved_contacts}
        self.group_entity = self.client.get_entity(self.config['group'])

        # Build the contact list
        self._build_contact_list()

    def _build_contact_list(self):
        """Convert saved Telegram contacts into a list of dictionaries."""
        self.contact_list = []  # Reset list to avoid duplicates

        for contact in self.saved_contacts:
            contact_info = {
                'user_id': contact.id,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'access_hash': contact.access_hash
            }
            if contact.phone:  # Only add phone if it exists
                contact_info['phone'] = contact.phone
            self.contact_list.append(contact_info)

    def _process_phone_number(self, phone):
        """Process a single phone number."""
        try:
            # Import contact to check registration
            contact = InputPhoneContact(client_id=0, phone=phone, first_name="Temp", last_name="Contact")
            result = self.client(ImportContactsRequest([contact]))

            if not result.users:
                print(f"❌ {phone}: Not registered on Telegram")
                self.results_report.append({'phone': phone, 'status': 'Not registered on Telegram'})
                return

            user = result.users[0]
            is_temp = user.id not in self.saved_contact_ids  # Check if contact is temporary

            # Try adding to group
            try:
                self.client(InviteToChannelRequest(
                    channel=self.group_entity,
                    users=[InputUser(user.id, user.access_hash)]
                ))
                print(f'⏳ Attempted to add {phone} to the group.')

                # Check if the user is a member of the group
                participants = self.client(GetParticipantsRequest(
                    channel=self.group_entity,
                    filter=ChannelParticipantsSearch(''),
                    offset=0,
                    limit=100,
                    hash=0
                ))

                # Check if the user is in the participants list
                user_is_member = any(participant.id == user.id for participant in participants.users)
                if user_is_member:
                    print(f"✅ {phone}: Added to group successfully.")
                    self.results_report.append({'phone': phone, 'status': 'Added to group successfully'})
                else:
                    print(f"❌ {phone} is limited to adding to groups or channels.")

                    try:
                        # Randomly select an invite message
                        invite_message = random.choice(self.config['invite_messages']).strip()
                        print(invite_message)

                        self.client.send_message(user.id,
                                                 invite_message.format(invite_link=self.config['invite_link']))
                        print(f"📩 {phone}: Privacy restricted - Invite sent via PM")
                        self.results_report.append(
                            {'phone': phone, 'status': 'Limited to adding to groups or channels. Invite sent via PM'})
                    except Exception as e:
                        print(f"⚠️ {phone}: Couldn't send message - {str(e)}")
                        self.results_report.append({'phone': phone, 'status': 'Could not send invite via PM'})

            except FloodWaitError as e:
                print(f"⏳ Flood wait for {phone}: Waiting {e.seconds} seconds")
                time.sleep(e.seconds)

            except Exception as e:
                print(f"⚠️ {phone}: Error adding to group - {str(e)}")
                self.results_report.append({'phone': phone, 'status': 'Error adding to group'})

            # Clean up temporary contact
            if is_temp:
                self.client(DeleteContactsRequest(id=[InputUser(user.id, user.access_hash)]))
            else:
                # Find matching contact from class-level contact_list
                matching_contact = next((contact for contact in self.contact_list if contact['user_id'] == user.id),
                                        None)
                if matching_contact:
                    # Handle None values in names
                    first_name = matching_contact['first_name'] or ''
                    last_name = matching_contact['last_name'] or ''

                    self.matches.append({
                        'phone': phone,
                        'user_id': user.id,
                        'first_name': first_name,
                        'last_name': last_name
                    })

        except Exception as e:
            print(f"⚠️ Critical error with {phone}: {str(e)}")
            self.results_report.append({'phone': phone, 'status': 'Critical error'})

    def _update_contacts(self):
        """Update contact information for matched contacts."""
        print(50 * '-')
        print("🔄️ Updating contacts name...")

        for match in self.matches:
            try:
                contact = InputPhoneContact(
                    client_id=0,
                    phone=match['phone'],
                    first_name=match['first_name'],
                    last_name=match['last_name']
                )
                self.client(ImportContactsRequest([contact]))
                print(f"🔄️ Updated contact: {match['first_name']} {match['last_name']} ({match['phone']})")
            except Exception as e:
                print(f"❌ Error updating {match['first_name']} {match['last_name']}: {e}")

    def _generate_report(self):
        """Generate an Excel report with the results."""
        df = pd.DataFrame(self.results_report)
        report_path = 'telegram_group_report.xlsx'
        df.to_excel(report_path, index=False)
        print(50 * '-')
        print(f"✅ Report generated: {report_path}")

    def run(self):
        """Main method to process all phone numbers."""
        self._initialize_client()

        total_numbers = len(self.phone_numbers)  # Total number of phone numbers
        for index, phone in enumerate(self.phone_numbers, start=1):
            print(f"---------------------- {index} / {total_numbers} ----------------------")
            self._process_phone_number(phone)
            time.sleep(int(self.config['delay']) + random.uniform(0, 2))  # Add delay between processing

        self._update_contacts()
        self._generate_report()  # Generate the report after processing

        print(50 * '-')
        print("Processing complete.")


if __name__ == "__main__":
    try:
        manager = TelegramGroupManager()
        manager.run()
    except Exception as e:
        print(f"❌ Error: {e}")