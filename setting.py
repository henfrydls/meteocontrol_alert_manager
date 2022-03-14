"""Settings file for managing login info and encrypting"""

from cryptography.fernet import Fernet
import sqlite3
import pyperclip as pc
import re


SERVERS_DICT = {"imap.gmail.com":"Gmail"}
TABLE_NAME = "Users"

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
    pc.copy(str(key)[2:-1])

    fernet = Fernet(key)
    encpassword = fernet.encrypt(password.encode())

    print(f"\nYour password key have been copied to clipboard!") 
    print(f"Key: {str(key)[2:-1]}")
    print("Save it somewhere secure and private!")  

    # Return encpassword and key in tuple
    return (str(encpassword)[2:-1], password)


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
        elif choice.lower() == "n":
            return False


def saving_info(email: str, server: str, server_name: str, encpasswd: str) -> None:
    """Save provided mail, server, and password to a database"""

    connection = sqlite3.connect("resources/users.sqlite")
    # Creating a way to send and recieve commands
    cur = connection.cursor()

    cur.executescript(f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}
                (user_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                user TEXT UNIQUE,
                server TEXT, 
                server_name TEXT,
                encpasswd TEXT
                );
                """)

    cur.execute('''INSERT INTO Users 
        (user, server, server_name, encpasswd)
		VALUES (?, ?, ?, ?)''', (email, server, server_name, encpasswd, ))

    connection.commit()
    connection.close()
    

def show_registered_users() -> dict:
    """Get user_id and user from table Users"""

    connection = sqlite3.connect("resources/users.sqlite")
    # Creating a way to send and recieve commands
    cur = connection.cursor()
    
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';")
    response = cur.fetchone()
    if response != None:
        users = dict()

        cur.execute("SELECT COUNT(user_id) FROM Users")
        registered_users = int(cur.fetchone()[0])
        cur.execute(("SELECT user_id, user FROM Users"))

        for _ in range(registered_users):
            user = cur.fetchone()
            users[user[0]] = user[1]
        
        connection.close()

        return users
    else:
        return False


def update_existing_password(user_id: int, encpassword: str) -> None:
    """Update password"""

    connection = sqlite3.connect("resources/users.sqlite")
    # Creating a way to send and recieve commands
    cur = connection.cursor() 

    cur.execute("UPDATE Users SET encpasswd = ? WHERE user_id = ?", (encpassword, user_id))
    connection.commit()
    connection.close()


def settings_loop() -> None:
    """Set email and password, change password and display information."""

    ACTIVE : bool = True

    while True:
        options = input("""
        What do you want to do?
        1. Set email and password
        2. Change password
        3. Show all login info
        \nResponse: """)
        print("\n")

        if options == "1":
            print("\nWARNING: Login info will be replaced.\n")
            while ACTIVE:
                EMAIL : str = input("\nEmail: ").strip().lower()
                if email_checker(EMAIL):
                    SERVER: str = setting_server()
                    ENCPASSWORD, PASSWORD = password_manager(input("\nPassword: "))
                else:
                    continue
                if conf_summary(EMAIL, SERVER, PASSWORD):
                    saving_info(EMAIL, SERVER, SERVERS_DICT[SERVER], ENCPASSWORD)
                    ACTIVE = False

        elif options == "2":
            users = show_registered_users()
            if users:
                print("\nWARNING: A new encryting key will be generated.\n")
                print("Choose an user_id.\n")
                for user_id, user in users.items():
                    print(f"{user_id} - {user}")

                while True:
                    response = int(input("\nResponse: "))
                    if response not in list(users.keys()):
                        print("Please select a valid user_id\n")
                        continue
                    break

                new_password = input("\nNew password: ")
                ENCPASSWORD, PASSWORD = password_manager(new_password)
                update_existing_password(response, ENCPASSWORD)

            else:
                print("There are not users registered yet.\n")

        elif options == "3":
            users = show_registered_users()
            if users:
                for user_id, user in users.items():
                    print(f"{user_id} - {user}")
            else:
                print("There are not users registered yet.\n")
        
        else:
            break

""" if __name__ == "__main__":
    welcome()
    settings_loop() """

welcome()
settings_loop()