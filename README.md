
# Telegram Members Adder

This project is a Python script designed to automate the process of adding users to a Telegram group using their mobile numbers. The script reads phone numbers from an Excel file, adds them to your Telegram contacts, and then invites them to a specified Telegram group. It also handles privacy restrictions, updates contact names, and generates a detailed report of the process.


## Features

- **Read Phone Numbers**: Reads phone numbers from an Excel file (column named `phone`).
- **Add Contacts**: Adds phone numbers to your Telegram contacts.
- **Invite to Group**: Invites contacts to a specified Telegram group.
- **Privacy Handling**: If a user has privacy restrictions, the script sends them an invite link via private message.
- **Contact Management**:
  - Updates the names of previously saved contacts to their original names.
  - Deletes temporary contacts to avoid cluttering your contact list.
- **Anti-Ban Measures**: Implements methods to prevent your Telegram account from being banned (e.g., delays between actions, handling rate limits).
- **Report Generation**: Generates an Excel report with the status of each number:
  - Successfully added to the group.
  - Restricted from being added (invite sent via private message).
  - Not registered on Telegram.


## Technologies and Libraries Used

- **Python**: The core programming language used for scripting.
- **Telethon**: A Python library for interacting with the Telegram API.
- **Pandas**: Used for reading and processing Excel files.
- **ConfigParser**: Manages configuration settings from a `config.ini` file.
- **JSON**: Stores and manages invite messages in a separate file (`invite_messages.json`).


## How It Works

1. **Configuration**:
   - The script reads configuration settings from a `config.ini` file, including:
     - Telegram API credentials (`api_id`, `api_hash`).
     - Your phone number.
     - Group username and invite link.
     - Path to the Excel file containing phone numbers.
     - Delay and retry settings to prevent bans.

2. **Phone Number Processing**:
   - The script reads phone numbers from the Excel file and adds them to your Telegram contacts.
   - It checks if the numbers are registered on Telegram.
   - For registered users, it attempts to add them to the specified group.

3. **Privacy Restrictions**:
   - If a user has privacy restrictions, the script sends them an invite link via private message using a randomly selected message from `invite_messages.json`.

4. **Contact Management**:
   - The script updates the names of previously saved contacts to their original names.
   - Temporary contacts (added during the process) are deleted to keep your contact list clean.

5. **Report Generation**:
   - After processing all numbers, the script generates an Excel report (`telegram_group_report.xlsx`) with the status of each number.


## Managing Invite Messages

Invite messages are stored in the `invite_messages.json` file. You can add or modify the messages in this file without changing the code. Each message should include the placeholder `{invite_link}` for the group invite link.

### Example `invite_messages.json`:
```json
[
    "Hi! Join our amazing group: {invite_link}",
    "Hey, we'd love to have you. Check it out here: {invite_link}",
    "Hello! Join our community: {invite_link}",
    "Welcome! Join us here: {invite_link}"
]
```


 To generate a variety of invite messages, you can use AI tools like GPT-based models with the following prompt:

### Prompt for Generating Invite Messages:

```
Generate a list of unique and friendly Telegram group invite messages formatted as a JSON-like array. Each message should contain a placeholder for a group invite link, such as {invite_link}. Ensure each message sounds conversational and distinct to avoid any spam flags.

Example output format:

[
  "Hi! Join our amazing group: {invite_link}",
  "Hey, we'd love to have you. Check it out here: {invite_link}"
]
```

Copy the generated messages and paste them directly into the `invite_messages.json` file.

### Example `invite_messages.json`:
```json
[
  "Hello! Our group is full of fun and interesting discussions. Don’t miss out: {invite_link}",
  "Hey there! Our group is all about sharing and learning together. Join us: {invite_link}",
  "Hi there! Our group is the place to be for all things exciting. Join us now: {invite_link}",
]
```


## Setup and Usage

### Prerequisites
- Python 3.x
- Telegram API credentials (`api_id` and `api_hash`).

### Installation
1. Clone the repository:
   ```bash
   git  clone https://github.com/SMR-H/Telegram-Members-Adder.git
   cd Telegram-Members-Adder
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `config.ini` file with the following structure:
   ```ini
   [Telegram]
   api_id = 12345678                  ; Your Telegram API ID (e.g., 12345678)
   api_hash = abcdef1234567890abcdef  ; Your Telegram API Hash (e.g., abcdef1234567890abcdef)
   phone = +1234567890                ; Your phone number with country code (e.g., +1234567890)
   group = @mygroup                   ; The username of your Telegram group (e.g., @mygroup)
   invite_link = https://t.me/+AbCdEfGhIjKlMnOp  ; The invite link for your group
   excel_file = phone_numbers.xlsx    ; Path to your Excel file containing phone numbers
   delay = 5                          ; Delay (in seconds) between processing each number
   max_retries = 3                    ; Maximum number of retries for failed operations
   ```

4. Prepare an Excel file (`phone_numbers.xlsx`) with a `phone` column containing the phone numbers you want to process.

5. Run the script:
   ```bash
   python tg_adder.py
   ```


## Example Report

The script generates an Excel report (`telegram_group_report.xlsx`) with the following columns:
- **Phone**: The phone number processed.
- **Status**: The result of the operation (e.g., "Added to group successfully", "Invite sent via PM", "Not registered on Telegram").


## Anti-Ban Measures

To prevent your Telegram account from being banned, the script includes the following features:
- **Delays**: Adds a delay between processing each phone number.
- **Rate Limit Handling**: Automatically handles rate limits (e.g., `FloodWaitError`).
- **Randomized Messages**: Uses a random invite message from `invite_messages.json` to avoid detection as spam.


## Contributing

We welcome contributions from everyone! If you have suggestions, improvements, or new features to add, feel free to open an issue or submit a pull request. Here’s how you can contribute:

1. **Fork this repository**
2. **Make Your Changes:** Add features, fix bugs, or improve the code in your fork.
3. **Create a Pull Request:** Submit a PR with a clear description of your changes.
4. **Review and Merge:** Your PR will be reviewed and merged once approved.


## ⚠️ Disclaimer

**Please Note**: This is a research project. I am by no means responsible for any usage of this tool. Use it at your own discretion. I'm also not responsible if your accounts get banned due to extensive use of this tool.


## ⚠️ Scam Alert

Some scammers are selling this free script and scamming people for money. **You don't need to pay anyone for this script**. It is freely available on GitHub for everyone to use and modify.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

