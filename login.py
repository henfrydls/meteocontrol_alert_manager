from sql_manager import Data
from password import Password
import imaplib


class Login:
    def __init__(self) -> None:
        DT = Data()
        self.username, self.encpassword, self.key, self.server = DT.login_info()
        if self.username is not None:
            PW = Password()
            self.password = PW.password_solver(self.encpassword, self.key)
            self.monitoring_email = "bluelog@meteocontrol.com"
        
    def login(self) -> bool:
        # create an IMAP4 class with SSL 
        self.imap = imaplib.IMAP4_SSL(self.server)
        try:
            self.imap.login(self.username, self.password)
            return True
        except:
            return False

    def messages(self) -> int:
        _, messages = self.imap.select("INBOX")
        # total number of emails
        messages = int(messages[0])
        # number of top emails to fetch
        N = messages
        return N

    def fetch(self, i) -> None:
        # fetch the email message by ID
        _, msg = self.imap.fetch(str(i), "(RFC822)")
        return msg

    def __del__(self):
        pass
        # close the connection and logout
        #self.imap.close()
        #self.imap.logout()