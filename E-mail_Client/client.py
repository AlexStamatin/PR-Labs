import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465 # ssl port 465, tls port 587

IMAP_SERVER =  'imap.gmail.com'
IMAP_PORT = 993

imap_client = 0
smtp_client = 0
login_nick = ""

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


def read(imap):
    # Login to INBOX
    # imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    # imap.login(username, password)
    imap.select('INBOX')

    status, response = imap.search(None, 'ALL')
    unread_msg_nums = response[0].split()

    # Print all unread messages from a certain sender of interest
    status, response = imap.search(None, '(ALL)')
    unread_msg_nums = response[0].split()
    da = []
    for e_id in unread_msg_nums:
        _, response = imap.fetch(e_id, '(RFC822)')
        da.append(email.message_from_bytes(response[0][1]))

    return da,len(unread_msg_nums)


def attachments(mail):
    nr = 0
    if mail.get_content_maintype() != 'multipart':
        return
    for part in mail.walk():
        if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
            nr += 1
    return nr


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


def sendMail(server,nick, to, subject, text, files=[]):

    assert type(files)==list

    msg = MIMEMultipart()
    msg['From'] = nick
    msg['To'] = to
    msg['Subject'] = subject

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

    server.quit()




def print_menu():       ## Your menu design here
    print('\n')
    print('Menu:')
    print("1.Log in")
    print("2.Show inbox")
    print("3.Select message to read")
    print("4.Send message")


while True:
    print_menu()
    choice=int(input("Enter Option: "))
    if choice == 1:
        smtp_client,imap_client = login("pyclient27@gmail.com","prstudent14")
    elif choice == 2:
        mes, nrmes = read(imap_client)

        for iter in range(nrmes):
            print(iter,".")
            print('Sender: ', mes[iter]["From"])
            print('Date: ', mes[iter]["Date"])
            print('Subject: ', mes[iter]["Subject"])
            nratt = attachments(mes[iter])
            prev = preview(mes[iter])
            if nratt != 0:
                print('Number of attachments: ', nratt)
            print('Preview: ', prev)
    elif choice == 3:
        mes, nrmes = read(imap_client)
        if nrmes != 0:
            print(nrmes,' messages avaialable')
            which = int(input('Message to read: '))
            if which > 0 and which <nrmes:
                body = readmes(mes[which-1])
                print(body)
            else:
                print('Outside range')
        else:
            print('No messages to read')

    elif choice == 10:
        break
