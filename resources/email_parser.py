import email
from email.header import decode_header
import re
from resources.sql_manager import Alerts
from resources.login import Login

class Parse:
    def __init__(self) -> None:
        self.LG = Login()
        self.AL = Alerts()

    @property
    def info(self) -> bool:
        return self.LG.username

    @property
    def messages(self) -> bool:
        return self.LG.messages()

    def __del__(self) -> None:
        print(f"{__name__} being deleted")


    def clean(self, text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)


    def extraction(self, body, ind):
        """Function to extract and clean alerts, based on meteocontrol bluelog
        firmware version. if ind is 3 its an error"""
        
        #Using regular expresion to extract coincidences 
        if ind == 1:
            time, description, state, device, name = re.findall("(?<=Timestamp: )(.*?)(?= \r)", body), \
            re.findall("(?<=Description: )(.*?)(?= \r)", body), re.findall("(?<=State: )(.*?)(?= \r)", body), \
                re.findall("(?<=Device: )(.*?)(?= \r)", body), re.findall("(?<=Plant name: )(.*)", body)
        elif ind == 2:
            time, description, state, device, name = [(body.split("\r\n\r\n")[0].split("\r\n")[0])], \
                ["".join(re.findall("(?<=Code: )(.*?)(?=\r)", body)), \
                "".join(re.findall("(?<=Additional information: )(.*)", body))] , \
                [None], [re.findall("(?<=Logger name: )(.*?)(?=\r)", body), re.findall("(?<=Device: )(.*?)(?=\r)", body)], \
                    re.findall("(?<=Plant name: )(.*?)(?=\r)", body)

            # Joining multiples information due to old firmware version
            time = [time[0].replace(" ", ", ")]
            description = [" ".join(description)]
            device = [": ".join([" ".join(list_) for list_ in device])]

        else:
            time = state = device = name = 404
            description = body

        return(time, description, state, device, name)


    def storing(self, info_pack, id):
        """Temporary non-formatted way of storing"""
        
        time, description, state, device, name = info_pack
        print(name)
        
        self.AL.storing_alerts(id, "".join(time), description,
                                state, device, name)


    def clasifing(self, body):
        """Function to clasify the alert base on the firmware version."""
        # eliminating useless information
        body = body.split("This is an automatically generated message")[0].strip()

        amount_multiple_message_body = body.split("\r\n\r\n")
        raw_id = amount_multiple_message_body[0]

        if "sn: " in raw_id:
            id, ind = int(raw_id.split("sn: ")[1].rsplit(")")[0]), 1
        elif "The blue'Log with the serial number" in raw_id:
            id, ind = "".join(re.findall("([0-9]+)", raw_id)), 2
        else:
            id, ind = "error", 3
        return(id, ind, amount_multiple_message_body)

    def sub_main(self, body, debug=True):
        """This function controls the general flow of the program behavior
        after email body are parsed"""

        #Extrating id and amount of message on a single body
        id, ind, amount_multiple_message_body = self.clasifing(body)
        self.AL.creating_table(id)

        if debug:
            if ind == 3:
                print(body)

        # Iterating through every message on a body
        for i in range(1, len(amount_multiple_message_body)):
            info_pack = self.extraction(amount_multiple_message_body[i], ind)
            # Temporary way of storing formated data
            self.storing(info_pack, id)
            

    def parsing(self, N) -> None:
        for i in range(N, N-N, -1):
            msg = self.LG.fetch(i)
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    # cleaning from
                    from_clean = (((From.split("<"))[1]).split(">")[0])
                    # just review emails comming from a particular source
                    if (from_clean.strip() == self.LG.monitoring_email):
                        # if the email message is multipart
                        if msg.is_multipart():
                            # iterate over email parts
                            for part in msg.walk():
                                # extract content type of email
                                content_type = part.get_content_type()
                                try:
                                    # get the email body
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    pass
                                if content_type == "text/plain":
                                    self.sub_main(body)       
                        else:
                            # extract content type of email
                            content_type = msg.get_content_type()
                            # get the email body
                            body = msg.get_payload(decode=True).decode()
                            if content_type == "text/plain":
                                self.sub_main(body)

if __name__ == "__main__":
    x = Parse()
    x.parsing(10)