import os
import sys
import logging
from password_manager.password_manager_api import PasswordManagerAPI
from password_manager.utils.verification_utils import VerificationUtils

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_input(prompt: str, sensitive: bool = False) -> str:
    """Gets input from the user, hiding it if sensitive."""
    if sensitive:
        try:
            import getpass
            return getpass.getpass(prompt)
        except (ImportError, RuntimeError):
            print("Warning: getpass module not available. Password will be visible.")
            return input(prompt)
    else:
        return input(prompt)

def display_message(message: str, is_error: bool = False):
    """Displays a message and waits for user confirmation."""
    prefix = "ERROR: " if is_error else ""
    print(f"\n{prefix}{message}\n")
    get_user_input("Press Enter to continue...")

def display_entries(entries: list[dict]):
    """Displays a formatted list of password entries."""
    if not entries:
        print("\nNo entries found.")
    else:
        print("\n--- Your Password Entries ---")
        for i, entry in enumerate(entries):
            print("-" * 50)
            print(f"Entry ID: {entry.get('id', 'N/A')} (Display No: {i+1})")
            print(f"  Name: {entry.get('Name', 'N/A')}")
            print(f"  Address: {entry.get('Address', 'N/A')}")
            print(f"  Username: {entry.get('Username', 'N/A')}")
            print(f"  Password: {'*' * len(entry.get('Password', ''))} (hidden)")
            print(f"  Notes: {entry.get('Notes', 'N/A')}")
        print("-" * 50)
    get_user_input("Press Enter to continue...")

def main_menu_pre_login():
    """Displays the menu for non-logged-in users."""
    clear_screen()
    print("--- Password Manager ---")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    print("------------------------")
    return get_user_input("Enter your choice: ")

def main_menu_post_login(username: str):
    """Displays the menu for logged-in users."""
    clear_screen()
    print(f"--- Welcome, {username}! ---")
    print("1. Add New Entry")
    print("2. View All Entries")
    print("3. View Specific Entry Details")
    print("4. Edit An Entry")
    print("5. Remove An Entry")
    print("6. Change Master Password")
    print("7. Generate Random Password")
    print("8. Logout")
    print("9. Exit")
    print("------------------------")
    return get_user_input("Enter your choice: ")

def register_user(api: PasswordManagerAPI):
    """Handles the user registration process."""
    clear_screen()
    print("--- Register New User ---")
    username = get_user_input("Enter desired username: ")
    password = get_user_input("Enter master password: ", sensitive=True)
    
    strength_info = VerificationUtils.check_password_strength(password)
    if not strength_info['is_strong']:
        print("Weak password detected:")
        for feedback_msg in strength_info['feedback']:
            print(f"- {feedback_msg}")
        if get_user_input("Do you want to use this weak password? (yes/no): ").lower() != 'yes':
            display_message("Registration cancelled.", is_error=True)
            return

    confirm_password = get_user_input("Confirm master password: ", sensitive=True)
    if password != confirm_password:
        display_message("Passwords do not match.", is_error=True)
        return

    success, message = api.register_user(username, password)
    display_message(message, not success)

def login_user(api: PasswordManagerAPI):
    """Handles the user login process."""
    clear_screen()
    print("--- Login ---")
    username = get_user_input("Enter username: ")
    password = get_user_input("Enter master password: ", sensitive=True)
    success, message = api.login_user(username, password)
    display_message(message, not success)

def add_entry(api: PasswordManagerAPI):
    """Handles adding a new password entry."""
    clear_screen()
    print("--- Add New Password Entry ---")
    name = get_user_input("Entry Name (e.g., Google): ")
    address = get_user_input("Website/URL (e.g., https://google.com): ")
    username_entry = get_user_input("Username for this entry: ")
    password_entry = get_user_input("Password for this entry: ", sensitive=True)
    notes = get_user_input("Notes (optional): ")

    success, message = api.add_entry(name, address, username_entry, password_entry, notes)
    display_message(message, not success)

def view_entries(api: PasswordManagerAPI):
    """Handles viewing all password entries."""
    clear_screen()
    success, entries_or_error = api.view_entries()
    if success:
        if isinstance(entries_or_error, list):
            display_entries(entries_or_error)
        else:
            # This case should ideally not be hit if API returns correctly
            display_message("Received unexpected data for entries.", is_error=True)
    else:
        display_message(entries_or_error, is_error=True)

def view_specific_entry_details(api: PasswordManagerAPI):
    """Allows viewing full details of a specific entry."""
    clear_screen()
    print("--- View Specific Entry Details ---")
    # First, show the list of entries so the user knows which ID to pick
    success, entries = api.view_entries()
    if not success or not isinstance(entries, list) or not entries:
        display_message("No entries available to view.", is_error=True)
        return
    
    display_entries(entries) 
    
    try:
        entry_id_input = get_user_input("Enter the ID of the entry to view: ")
        entry_id = int(entry_id_input)
    except ValueError:
        display_message("Invalid ID. Please enter a number.", is_error=True)
        return

    success, entry_or_error = api.get_entry_by_id(entry_id)
    if success and isinstance(entry_or_error, dict):
        clear_screen()
        print(f"--- Details for Entry ID: {entry_or_error['id']} ---")
        for key, value in entry_or_error.items():
            if key not in ['id', 'EntryName']:
                 print(f"  {key}: {value}")
        print("-" * 50)
        display_message("Warning: Password has been displayed.")
    else:
        display_message(str(entry_or_error), is_error=True)

def edit_entry(api: PasswordManagerAPI):
    """Handles editing an existing entry."""
    clear_screen()
    success, entries = api.view_entries()
    if not success or not isinstance(entries, list) or not entries:
        display_message("No entries available to edit.", is_error=True)
        return
    display_entries(entries)

    try:
        entry_id_input = get_user_input("Enter the ID of the entry to edit: ")
        entry_id = int(entry_id_input)
    except ValueError:
        display_message("Invalid ID. Please enter a number.", is_error=True)
        return

    success, entry = api.get_entry_by_id(entry_id)
    if not success or not isinstance(entry, dict):
        display_message(str(entry), is_error=True)
        return

    print("\n--- Editing Entry --- (Press Enter to keep current value)")
    new_name = get_user_input(f"Name ({entry.get('Name')}): ") or entry.get('Name')
    new_address = get_user_input(f"Address ({entry.get('Address')}): ") or entry.get('Address')
    new_username = get_user_input(f"Username ({entry.get('Username')}): ") or entry.get('Username')
    new_password = get_user_input("New Password (leave blank to keep current): ", sensitive=True) or entry.get('Password')
    new_notes = get_user_input(f"Notes ({entry.get('Notes')}): ") or entry.get('Notes')

    success, message = api.edit_entry(entry_id, new_name, new_address, new_username, new_password, new_notes)
    display_message(message, not success)

def remove_entry(api: PasswordManagerAPI):
    """Handles removing an entry."""
    clear_screen()
    success, entries = api.view_entries()
    if not success or not isinstance(entries, list) or not entries:
        display_message("No entries to remove.", is_error=True)
        return
    display_entries(entries)

    try:
        entry_id_input = get_user_input("Enter the ID of the entry to remove: ")
        entry_id = int(entry_id_input)
    except ValueError:
        display_message("Invalid ID. Please enter a number.", is_error=True)
        return

    if get_user_input(f"Confirm removal of entry ID {entry_id}? (yes/no): ").lower() == 'yes':
        success, message = api.remove_entry(entry_id)
        display_message(message, not success)
    else:
        display_message("Removal cancelled.")

def change_master_password(api: PasswordManagerAPI):
    """Handles changing the master password."""
    clear_screen()
    print("--- Change Master Password ---")
    old_password = get_user_input("Enter current master password: ", sensitive=True)
    new_password = get_user_input("Enter new master password: ", sensitive=True)
    
    strength_info = VerificationUtils.check_password_strength(new_password)
    if not strength_info['is_strong']:
        print("Weak new password detected:")
        for msg in strength_info['feedback']:
            print(f"- {msg}")
        if get_user_input("Use weak password anyway? (yes/no): ").lower() != 'yes':
            display_message("Password change cancelled.", is_error=True)
            return

    if new_password != get_user_input("Confirm new master password: ", sensitive=True):
        display_message("New passwords do not match.", is_error=True)
        return

    success, message = api.change_master_password(old_password, new_password)
    display_message(message, not success)

def generate_random_password(api: PasswordManagerAPI):
    """Handles generating a random password."""
    clear_screen()
    print("--- Generate Random Password ---")
    try:
        length_input = get_user_input("Enter desired length: ")
        length = int(length_input)
    except ValueError:
        display_message("Invalid length. Please enter a number.", is_error=True)
        return

    use_uppercase = get_user_input("Include uppercase? (y/n): ").lower() == 'y'
    use_lowercase = get_user_input("Include lowercase? (y/n): ").lower() == 'y'
    use_digits = get_user_input("Include digits? (y/n): ").lower() == 'y'
    use_special = get_user_input("Include special characters? (y/n): ").lower() == 'y'

    success, password_or_msg = api.generate_random_password(length, use_uppercase, use_lowercase, use_digits, use_special)
    if success:
        display_message(f"Generated Password: {password_or_msg}")
    else:
        display_message(password_or_msg, is_error=True)

def main():
    """Main application loop."""
    # Configure logging for the application
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    api = PasswordManagerAPI()
    while True:
        if api.is_logged_in():
            choice = main_menu_post_login(api.current_username)
            actions = {
                '1': add_entry, '2': view_entries, '3': view_specific_entry_details,
                '4': edit_entry, '5': remove_entry, '6': change_master_password,
                '7': generate_random_password
            }
            if choice in actions:
                actions[choice](api)
            elif choice == '8':
                success, message = api.logout_user()
                display_message(message)
            elif choice == '9':
                display_message("Exiting Password Manager. Goodbye!")
                sys.exit()
            else:
                display_message("Invalid choice.", is_error=True)
        else:
            choice = main_menu_pre_login()
            if choice == '1':
                register_user(api)
            elif choice == '2':
                login_user(api)
            elif choice == '3':
                display_message("Exiting Password Manager. Goodbye!")
                sys.exit()
            else:
                display_message("Invalid choice.", is_error=True)

if __name__ == '__main__':
    main()
