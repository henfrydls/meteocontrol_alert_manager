from resources.sql_manager import Data
from resources.email_parser import Parse
from datetime import datetime

class Main:
    def __init__(self) -> None:
        self.PS = Parse()

        if not self.PS.info and self.PS.info is not None:
            print("""\nPlease go to setting.py and set/check your login info.\n""")
        else:
            self.messages = self.PS.messages
        
            self.DT = Data()
            self.messages_read = self.DT.registered_messages()[0]
            try:
                if int(self.messages_read) == self.messages:
                    print("\nYou are up to date!\n")
            except:
                if self.messages_read is not None:
                    self.PS.parsing(self.messages - int(self.messages_read))
                else:
                    self.PS.parsing(self.messages)

            # Create a time stamp
            time = datetime.now()
            self.DT.updating_messages(time, self.messages)

    def __del__(self):
        print(f"\n{__name__} being destroyed")


if __name__ == "__main__":
    Main()

