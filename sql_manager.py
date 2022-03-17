import sqlite3

class SQL_Users:
    def __init__(self, location="resources/users.sqlite") -> None:
        self.connection = sqlite3.connect(location)
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
                    server TEXT, 
                    server_name TEXT,
                    encpasswd TEXT
                    );
                    """)

    def saving_info(self, email: str, server: str, server_name: str, encpasswd: str) -> None:
        """Save provided mail, server, and password to a database"""

        self.cur.execute('''INSERT INTO Users 
            (user, server, server_name, encpasswd)
            VALUES (?, ?, ?, ?)''', (email, server, server_name, encpasswd, ))

        self.connection.commit()

    def show_registered_users(self) -> dict:
        """Get user_id and user from table Users"""
        
        self.cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.TABLE_NAME}';")
        response = self.cur.fetchone()
        if response != None:
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
    
    def update_existing_password(self, user_id: int, encpassword: str) -> None:
        """Update password"""

        self.cur.execute("UPDATE Users SET encpasswd = ? WHERE user_id = ?", (encpassword, user_id))
        self.connection.commit()

class Data:
    def __init__(self, location="resources/data.sqlite") -> None:
        self.connection = sqlite3.connect(location)
        # Creating a way to send and recieve commands
        self.cur = self.connection.cursor()
        self.TABLE_NAME = "Data"
        self.creating_table()

    def __del__(self) -> None:
        print("Object being destroy")

    def creating_table(self) -> None:
        """Creates a table if it still does not exist"""
        self.cur.executescript(f"""CREATE TABLE IF NOT EXISTS {self.TABLE_NAME}
                    (id PRIMARY KEY AUTOINCREMENT UNIQUE,
                    last_update TEXT,
                    read_messages TEXT,
                    login_user INTEGER FOREING KEY UNIQUE);
                    """)

    def login_preferences(self, ind) -> None:
        """Change the FOREING KEY related to login"""
        
        self.cur.execute("SELECT last_update, read_messages FROM Data")
        last_update, read_messages = self.cur.fetchone()[0], self.cur.fetchone()[1] 

        self.cur.execute(f'''INSERT INTO Data
        (last_update, read_messages, login_user) VALUES (?, ?, ?)''', (last_update, read_messages, ind))
        
        self.connection.commit()

    def login_info(self):
        pass

