from resources.sql_manager import Data
from resources.password import Password
import imaplib

class Login:
    def __init__(self) -> None:
        DT = Data()
        self.username, self.encpassword, self.key, self.server = DT.login_info()
        self.monitoring_email = "bluelog@meteocontrol.com"
        if self.username and self.username is not None:
            self.password_solver()
            self.login()
            self.monitoring_email = "bluelog@meteocontrol.com"
            
    def login(self) -> bool:
        # create an IMAP4 class with SSL 
        self.imap = imaplib.IMAP4_SSL(self.server)
        self.imap.login(self.username, self.password)

    def password_solver(self):
        PW = Password()
        self.password = PW.password_solver(self.encpassword, self.key)

    def messages(self) -> int:
        _, messages = self.imap.select("INBOX")
        # total number of emails
        messages = int(messages[0])
        # number of top emails to fetch
        N = messages
        return N

    def fetch(self, i) -> None:
        _, messages = self.imap.select("INBOX")
        # fetch the email message by ID
        _, msg = self.imap.fetch(str(i), "(RFC822)")
        return msg

    def __del__(self):
        print(f"{__name__} being deleted")
        # close the connection and logout
        #self.imap.close()
        #self.imap.logout()