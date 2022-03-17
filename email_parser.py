import imaplib
import email
from email.header import decode_header
import json
import re
from sql_manager import Data

data = Data()

with open("account.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

username = jsonObject["email"]
password = jsonObject["password"]
meteocontrol = jsonObject["meteocontrol_email"]

# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
try:
    imap.login(username, password)
except:
    pass
status, messages = imap.select("INBOX")
# total number of emails
messages = int(messages[0])
# number of top emails to fetch
N = messages

verified_plant_names = list()

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def extraction(body, id, ind):
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
        description = [" ".join(description)]
        device = [": ".join([" ".join(list_) for list_ in device])]

    else:
        time = description = state = device = name = 404

    return(time, description, state, device, name)


def storing(info_pack, id):
    """Temporary non-formatted way of storing"""
    time, description, state, device, name = info_pack
    verified_plant_names.append(name)
    jsonFile_e = open(f".\monitoring\{id}.json", "a")
    for i in range(len(time)):
        jsonformat = {
            "Time":time[i],
            "Description":description[i],
            "State":state[i],
            "Device":device[i],
            "Plant Name":name[i]
        }
        jsonstring= json.dumps(jsonformat) 
        jsonFile_e.write(jsonstring)
        jsonFile_e.write(",")
    jsonFile_e.close()

def clasifing(body):
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

def main(body, debug=True):
    """This function controls the general flow of the program behavior
    after email body are parsed"""

    #Extrating id and amount of message on a single body
    id, ind, amount_multiple_message_body = clasifing(body)

    if debug:
        if ind == 3:
            print(body)

    # Iterating through every message on a body
    for i in range(1, len(amount_multiple_message_body)):
        info_pack = extraction(amount_multiple_message_body[i], id, ind)
        # Temporary way of storing formated data
        storing(info_pack, id)


for i in range(messages, messages-N, -1):
    print(f"{i}/{messages}")
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
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
            if (from_clean.strip() == meteocontrol):
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
                            main(body)       
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        main(body)

for plan_name in verified_plant_names:
    print(plan_name)

# close the connection and logout
imap.close()
imap.logout()