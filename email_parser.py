import imaplib
import email
from email.header import decode_header
import os
import json
import re

with open("account.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

username = jsonObject["email"]
password = jsonObject["password"]
meteocontrol = jsonObject["meteocontrol_email"]

# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
imap.login(username, password)
status, messages = imap.select("INBOX")
# total number of emails
messages = int(messages[0])
# number of top emails to fetch
N = messages

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def extraction(body, id, ind):
    if ind == 1:
        time, description, state, device, name = re.findall("(?<=Timestamp: )(.*?)(?= \r)", body), \
        re.findall("(?<=Description: )(.*?)(?= \r)", body), re.findall("(?<=State: )(.*?)(?= \r)", body), \
            re.findall("(?<=Device: )(.*?)(?= \r)", body), re.findall("(?<=Plant name: )(.*)", body)
    elif ind == 2:
        time, description, state, device, name = [(body.split("\r\n\r\n")[0].split("\r\n")[0])], \
             ["".join(re.findall("(?<=Code: )(.*?)(?=\r)", body)), "".join(re.findall("(?<=Additional information: )(.*)", body))] , \
            [None], re.findall("(?<=Logger name: )(.*?)(?=\r)", body), re.findall("(?<=Plant name: )(.*?)(?=\r)", body)
    print(time, description, state, device, name)
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
    #return(body)

def clasifing(body):
    # eliminating useless information
    body = body.split("This is an automatically generated message")[0].strip()
    #id = serial_id(fomartted_body)
    # print text/plain emails and skip attachments
    #print({body})
    message_body = body.split("\r\n\r\n")
    raw_id = message_body[0]
    #print(f"\n{raw_id}")
    if "sn: " in raw_id:
        id, ind = int(raw_id.split("sn: ")[1].rsplit(")")[0]), 1
        #print(id)
    elif "The blue'Log with the serial number" in raw_id:
        id, ind = "".join(re.findall("([0-9]+)", raw_id)), 2
        #print("".join(id))
    else:
        id, ind = "error", 3
    for i in range(1, len(message_body)):
        #print(i)
        #print(f"{message_body[i]}")
        #print("\n\n")
        extraction(message_body[i], id, ind)

for i in range(messages, messages-N, -1):
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
                            clasifing(body)       
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        clasifing(body)
                #print("="*100)
# close the connection and logout
imap.close()
imap.logout()