from email import message
from resources.sql_manager import Data
from resources.email_parser import Parse
from datetime import datetime
from time import sleep

class Main:
    def __init__(self) -> None:
        self.PS = Parse()
        if not self.PS.info and self.PS.info is not None:
            print("""\nPlease go to setting.py and set/check your login info.\n""")
        else:
            print("hey1")
            self.messages = self.PS.messages
        
            self.DT = Data()
            self.messages_read = self.DT.registered_messages()[0]
            if self.messages is not None:
                if int(self.messages_read) == self.messages:
                    print("\nYou are up to date!\n")
                else:
                    messages_to_read = self.messages - int(self.messages_read)
                    self.PS.parsing(self.messages, messages_to_read)
            else:
                self.PS.parsing(self.messages, self.messages)

            # Create a time stamp
            time = datetime.now()
            self.DT.updating_messages(time, self.messages)

    def __del__(self):
        print(f"\n{__name__} being destroyed")


if __name__ == "__main__":
    while True:
        main = Main()
        del main
        sleep(60)
