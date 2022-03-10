"""Settings file for managing login info and encrypting"""

from cryptography.fernet import Fernet
import re
import pyperclip as pc

SERVERS_DICT = {"imap.gmail.com":"Gmail"}

def welcome() -> None:
    """Welcomen message to setting portal"""
    print("""
    Welcome to settings portal!
    In here you will be able to set your mail, imap server
    and password. Every password provided will be encrypted
    and you will have to save the provided key somewhere else!

    Select any non-asked value to quit.\n
    """)


def email_checker(email: str) -> bool:
    """Returns true if the passed value is a email"""
    response = bool(re.search('\S+@\S+[\w-]+\.+[\w-]{2,100}$', email))
    if not response:
        print("\t Please enter a valid emial.")
    return response


def setting_server() -> str:
    """Sets server"""

    print("\nAvailable Servers:")
    while True:
        for i, SERVER in enumerate(SERVERS_DICT.values()):
            print(f"\t{i+1} - {SERVER}")
        try:
            return(list(SERVERS_DICT.keys())[int(input("\nSelect Server: "))-1])
        except:
            print("Please select one of the options provide!")
            continue


def password_manager(password : str) -> tuple:
    """This function recieved a password and encrypted it"""
    # generate a key for encryption and decryption
    key = Fernet.generate_key()

    # Saving key on clipboard
    pc.copy(str(key))

    fernet = Fernet(key)
    encpassword = fernet.encrypt(password.encode())

    # Return encpassword and key in tuple
    return (encpassword, key, password)


def conf_summary(email: str, server: str, password: str) -> bool:
    """Checks if the user wants to keep the preious configuration."""
    print(f"""
    Do you want to keep this configuration?

    Email: {email}
    Server: {SERVERS_DICT[server]}
    Password: {password}
    """)
    while True:
        choice = input("\nY/N? ")
        if choice.lower() == "y":
            return True
        else:
            return False

def settings_loop() -> None:
    """Set email and password, change password and display information."""

    ACTIVE : bool = True

    while ACTIVE:
        options = input("""
        What do you want to do?
        1. Set email and password
        2. Change password
        3. Show previous login info
        """)

        if options == "1":
            print("\nWARNING: All previous login info will be lost.\n")
            while ACTIVE:
                EMAIL : str = input("\nEmail: ").strip().lower()
                if email_checker(EMAIL):
                    SERVER: str = setting_server()
                    ENCPASSWORD, KEY, PASSWORD = password_manager(input("\nPassword: "))
                    print(f"\nYour password key have been copied to clipboard!") 
                    print(f"Key: {KEY}")
                    print("Save it somewhere secure and private!")  
                else:
                    continue
                if conf_summary(EMAIL, SERVER, PASSWORD):

                    ACTIVE = False

if __name__ == "__main__":
    welcome()
    settings_loop()