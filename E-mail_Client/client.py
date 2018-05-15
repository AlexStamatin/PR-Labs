import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import getpass
import os

#gmail SSL SMTP Server

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465 # ssl port 465, tls port 587

#gmail SSL IMAP Server

IMAP_SERVER =  'imap.gmail.com'
IMAP_PORT = 993

#smtp and imap sessions

imap_client = 0
smtp_client = 0

#user nickname and password

login_nick = ""
login_pass = ""

#create connection with imap and smtp servers

def login(user, password):

    try:
        smtp_ssl = smtplib.SMTP_SSL(SMTP_SERVER,SMTP_PORT)
        smtp_ssl.login(user,password)

        imap_ssl = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        imap_ssl.login(user,password)

    except:
        print("Log in failed")
        return

    return smtp_ssl,imap_ssl



# returns number of messages and an array of messages from the mail inbox
# receives imap session as parameter
def read(imap):


    imap.select('INBOX')

    status, response = imap.search(None, 'ALL')
    unread_msg_nums = response[0].split()

    unread_msg_nums = response[0].split()
    nr = []
    for e_id in unread_msg_nums:
        _, response = imap.fetch(e_id, '(RFC822)')
        nr.append(email.message_from_bytes(response[0][1]))

    return nr,len(unread_msg_nums)


#returns messages which contaned searched string in either sender or subject
def search(imap,string):

    imap.select('INBOX')

    status, response = imap.search(None, 'ALL')
    unread_msg_nums = response[0].split()

    # sort messages
    status, response = imap.search(None, 'ALL', '(OR (FROM "%s") (SUBJECT "%s"))' % (string,string))
    unread_msg_nums = response[0].split()
    nr = []
    for e_id in unread_msg_nums:
        _, response = imap.fetch(e_id, '(RFC822)')
        nr.append(email.message_from_bytes(response[0][1]))

    return nr,len(unread_msg_nums)

#returns number of attachments of an email
def attachments(mail):
    nr = 0
    if mail.get_content_maintype() != 'multipart':
        return
    for part in mail.walk():
        if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
            nr += 1
    return nr

#reutns preview of the text content of the message
def preview(mail):
    body = ""
    if mail.is_multipart():
        for part in mail.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = mail.get_payload(decode=True)

    if body != "":
        body = body.decode()
        body = body.split('\n', 1)[0]

    return body

#returns full text body of a message
def readmes(mail):

    body = ""
    if mail.is_multipart():
        for part in mail.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = mail.get_payload(decode=True)

    if body != "":
        body = body.decode()

    return body

#checks if connection is still active
def test_conn_open(conn):
    try:
        status = conn.noop()[0]
    except:  # smtplib.SMTPServerDisconnected
        status = -1
    return True if status == 250 else False

#sends an email with optional attachments and cc fields
def sendMail(server,nick, to, subject, text, files=[],cc=None):

    assert type(files)==list

    msg = MIMEMultipart()
    msg['From'] = nick
    msg['Subject'] = subject
    msg['To'] = to
    if cc:
        msg['Cc'] = cc
        to.append(cc)
    to = [to]

    msg.attach(MIMEText(text))

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)

    server.sendmail(nick, to, msg.as_string())

    print('Done')

# def set_password(self, raw_password):
#     import random
#     algo = 'sha1'
#     salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
#     hsh = get_hexdigest(algo, salt, raw_password)
#     self.password = '%s$%s$%s' % (algo, salt, hsh)




def print_menu():       #Menu options
    print('\n')
    print('Menu:')
    print("1.Log in")
    print("2.Show inbox")
    print("3.Select message to read")
    print("4.Send message")
    print("5.Search")
    print("6.Exit")


while True:
    print_menu()
    choice=int(input("Enter Option: "))
    if choice == 1:
        login_nick = input("Nickname: ")
        login_pass = getpass.getpass("Password: ")
        smtp_client,imap_client = login(login_nick,login_pass)
    elif choice == 2:
        if not test_conn_open(imap_client):
            login(login_nick,login_pass)
        mes, nrmes = read(imap_client)

        for iter in range(nrmes):
            print(iter+1,".")
            print('Sender: ', mes[iter]["From"])
            print('Date: ', mes[iter]["Date"])
            print('Subject: ', mes[iter]["Subject"])
            nratt = attachments(mes[iter])
            prev = preview(mes[iter])
            if nratt != 0:
                print('Number of attachments: ', nratt)
            print('Preview: ', prev)
    elif choice == 3:
        if not test_conn_open(imap_client):
            login(login_nick,login_pass)
        mes, nrmes = read(imap_client)
        if nrmes != 0:
            print(nrmes,' messages avaialable')
            which = int(input('Message to read: '))
            if which > 0 and which <nrmes:
                body = readmes(mes[which-1])
                print(which-1, ".")
                print('Sender: ', mes[which-1]["From"])
                print('Date: ', mes[which-1]["Date"])
                print('Subject: ', mes[which-1]["Subject"])
                print(body)
            else:
                print('Outside range')
        else:
            print('No messages to read')
    elif choice == 4:
        if not test_conn_open(imap_client):
            login(login_nick,login_pass)
        recip = input("Recipient: ")
        subj = input("Subject: ")
        text = input("Text: ")
        cc = input("Additional recipients: ").upper()
        if cc == 'YES':
            address = input("cc address: ")
        else:
            address = None
        attach = input("Include files?: ").upper()
        files = []
        if attach == "YES":
            filename = input('Attachment name: ')
            files.append(filename)
        sendMail(smtp_client,login_nick, recip, subj, text, files, address)

    elif choice == 5:
        key = input("Search string: ")
        mes,nrmes = search(imap_client,key)
        if nrmes != 0:
            for iter in range(nrmes):
                print(iter,".")
                print('Sender: ', mes[iter]["From"])
                print('Date: ', mes[iter]["Date"])
                print('Subject: ', mes[iter]["Subject"])
                nratt = attachments(mes[iter])
                prev = preview(mes[iter])
        else:
            print("Nothing found")

    elif choice == 6:
        break
