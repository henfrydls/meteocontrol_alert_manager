"""Settings file for managing login info and encrypting"""

from re import search
from resources.sql_manager import Users, Data
from resources.password import Password


SERVERS_DICT = {"imap.gmail.com":"Gmail"}
User = Users()
data = Data()
PW = Password()


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
    response = bool(search('\S+@\S+[\w-]+\.+[\w-]{2,100}$', email))
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
            print(f"\n\tYour login info have been have been set!\n") 
            return True
        elif choice.lower() == "n":
            return False


def settings_loop() -> None:
    """Set email and password, change password and display information."""

    while True:
        options = input("""
        What do you want to do?
        1. Set email and password
        2. Change password
        3. Select user to login
        4. Show all login info
        \nResponse: """)
        print("\n")

        if options.strip() == "1":
            print("\nWARNING: Login info will be replaced.\n")
            while True:
                EMAIL : str = input("\nEmail: ").strip().lower()
                if email_checker(EMAIL):
                    SERVER: str = setting_server()
                    PASSWORD = input("\nPassword: ")
                    ENCPASSWORD, PASSWORD, KEY = PW.password_manager(PASSWORD)
                else:
                    continue
                if conf_summary(EMAIL, SERVER, PASSWORD):
                    User.saving_info(EMAIL, SERVER, SERVERS_DICT[SERVER], ENCPASSWORD, KEY)
                    users = User.show_registered_users()
                    if len(users.keys()) == 1:
                        data.login_preferences(1)
                break

        elif options.strip() == "2":
            users = User.show_registered_users()
            if users:
                print("\nWARNING: A new encryting key will be generated.\n")
                print("Choose an User ID.\n")
                for user_id, user in sorted(users.items()):
                    print(f"{user_id} - {user}")

                while True:
                    response = input("\nResponse: ")
                    if response not in str(list(users.keys())):
                        print("Please select a valid User ID\n")
                        continue
                    break

                new_password = input("\nNew password: ")
                ENCPASSWORD, _, KEY = PW.password_manager(new_password)
                User.update_existing_password(response, ENCPASSWORD, KEY)
                print("\nYour password have been updated!!!")

            else:
                print("There are not users registered yet.\n")

        elif options.strip() == "3":
            users = User.show_registered_users()
            if users:
                print("Select an email to login.\n")
                for user_id, user in sorted(users.items()):
                    print(f"{user_id} - {user}")

                while True:
                    response = input("\nResponse: ")
                    if response not in str(list(users.keys())):
                        print("Please select a valid User ID\n")
                        continue
                    break

                data.login_preferences(int(response))
                print(f"\nYour Login information have been update.\n")

            else:
                print("There are not users registered yet.\n")

        elif options.strip() == "4":
            users = User.show_registered_users()
            if users:
                for user_id, user in sorted(users.items()):
                    print(f"{user_id} - {user}")
            else:
                print("There are not users registered yet.\n")
        
        else:
            break

if __name__ == "__main__":
    
    welcome()
    settings_loop()
    
