import sqlite3
import os

class Users:
    def __init__(self) -> None:
        self.location = os.path.abspath(os.curdir)+"\\db\\user_data.sqlite"
        self.connection = sqlite3.connect(self.location)
        # Creating a way to send and recieve commands
        self.cur = self.connection.cursor()
        self.TABLE_NAME = "Users"
        self.creating_table()


    def __del__(self):
        print("Object being destroy")


    def creating_table(self) -> None:
        self.cur.executescript(f"""CREATE TABLE IF NOT EXISTS {self.TABLE_NAME}
                    (user_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    user TEXT UNIQUE,
                    server TEXT NOT NULL, 
                    server_name TEXT NOT NULL,
                    encpasswd TEXT NOT NULL,
                    key TEXT NOT NULL
                    );
                    """)


    def saving_info(self, email: str, server: str, server_name: str, encpasswd: bytes, key: bytes) -> None:
        """Save provided mail, server, and password to a database"""

        self.cur.execute('''INSERT INTO Users 
            (user, server, server_name, encpasswd, key)
            VALUES (?, ?, ?, ?, ?)''', (email, server, server_name, encpasswd, key))

        self.connection.commit()


    def show_registered_users(self) -> dict:
        """Get user_id and user from table Users"""
        
        self.cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.TABLE_NAME}';")
        response = self.cur.fetchone()
        if response is not None:
            users = dict()

            self.cur.execute("SELECT COUNT(user_id) FROM Users")
            registered_users = int(self.cur.fetchone()[0])
            self.cur.execute(("SELECT user_id, user FROM Users"))

            for _ in range(registered_users):
                user = self.cur.fetchone()
                users[user[0]] = user[1]

            return users
        else:
            return False
    

    def update_existing_password(self, user_id: int, encpassword: str, key:bytes) -> None:
        """Update password"""

        self.cur.execute("UPDATE Users SET encpasswd = ?, key = ? WHERE user_id = ?", 
                        (encpassword, key, user_id))
        
        self.connection.commit()

class Data:
    def __init__(self) -> None:
        self.location = os.path.abspath(os.curdir)+"\\db\\user_data.sqlite"
        self.connection = sqlite3.connect(self.location)
        # Creating a way to send and recieve commands
        self.cur = self.connection.cursor()
        self.TABLE_NAME = "Data"
        self.creating_table()


    def __del__(self) -> None:
        print(f"{__name__} being deleted")


    def creating_table(self) -> None:
        """Creates a table if it still does not exist"""
        self.cur.executescript(f"""CREATE TABLE IF NOT EXISTS {self.TABLE_NAME}
                    (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    last_update TEXT,
                    read_messages INTEGER,
                    login_user INTEGER FOREING KEY UNIQUE);
                    """)


    def login_preferences(self, ind) -> None:
        """Change the FOREING KEY related to login"""
        
        self.cur.execute("SELECT last_update, read_messages FROM Data")
        response = self.cur.fetchone()
        if response is not None:
            last_update, read_messages = response[0], response[1]
        else:
            last_update = read_messages = None 

        self.cur.execute(f'''REPLACE INTO Data
        (last_update, read_messages, login_user) VALUES (?, ?, ?)''', (last_update, read_messages, ind))
        
        self.connection.commit()


    def login_info(self) -> tuple:
        """Get login info based on user login preferences"""

        try:
            self.cur.execute("""SELECT Users.user, Users.encpasswd, Users.key, Users.server
                            FROM Data JOIN Users ON Data.login_user = Users.user_id
                            ORDER BY Data.id DESC LIMIT 1;""")
            response = self.cur.fetchone()
        except sqlite3.OperationalError:
            response =  (False, False, False, False)
        return(response)


    def registered_messages(self) -> tuple:
        """Read the amount of messages there have been read"""

        self.cur.execute("""SELECT read_messages FROM Data;""")
        response = self.cur.fetchone()
        return(response)

    def updating_messages(self, last_update, read_messages) -> None:
        """Updates the amount of messages read and its time"""

        self.cur.execute("SELECT login_user FROM Data")
        login_user = self.cur.fetchone()[0]

        self.cur.execute(f'''REPLACE INTO Data
        (last_update, read_messages, login_user) VALUES (?, ?, ?)''', (last_update, read_messages, login_user))

        self.connection.commit()

class Alerts:
    def __init__(self) -> None:
        self.location = os.path.abspath(os.curdir)+"\\db\\alerts.sqlite"
        self.connection = sqlite3.connect(self.location)
        # Creating a way to send and recieve commands
        self.cur = self.connection.cursor()
        self.TABLE_NAME = "Alerts"
    
    def creating_table(self, id) -> None:
        self.cur.executescript(f"""CREATE TABLE IF NOT EXISTS '{id}'
                    (time TEXT,
                    description TEXT,
                    state TEXT,
                    device TEXT, 
                    name TEXT);
                    """)

    def storing_alerts(self, id, time, description, state, device, name) -> None:
        self.cur.execute(f"""INSERT INTO '{id}'
            (time, description, state, device, name)
            VALUES (?, ?, ?, ?, ?)""",
            (time, description[0], state[0], device[0], name[0],))

        self.connection.commit()

    def __del__(self):
        print(f"{__name__} being deleted")