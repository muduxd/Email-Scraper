import mysql.connector
import imaplib
import email
import sys
import csv


mydb = None

try:
    mydb = mysql.connector.connect(
        user = "root",
        host = "localhost",
        database = "email_scraper"
    )

except:
    sys.exit("Unable To Connect To The Database!\n")



def scrape(user, password):
    imap_url = "imap.gmail.com"
    mail = imaplib.IMAP4_SSL(imap_url)


    try:
        mail.login(user, password)
    except:
        print("Invalid Credentials!\n")
        return
    

    status, messages = mail.select("Inbox")

    if status != "OK": 
        exit("Invalid Credentials!\n")


    mycursor = mydb.cursor()
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS `{}` (SENDER VARCHAR(100), SUBJECT VARCHAR(100), BODY VARCHAR(255))".format(user))
    except:
        print("Cannot Create The Table!\n")
        return

    print("")
    for i in range(1, int(messages[0])):
        status, msg = mail.fetch(str(i), '(RFC822)')

        if status == "OK":
            for response in msg:
                if isinstance(response, tuple):

                    email_message = email.message_from_bytes(msg[0][1])
                    sender = str(email.header.make_header(email.header.decode_header(email_message['From'])))
                    subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
                    body = ""


                    if email_message.is_multipart():
                        for part in email_message.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get('Content-Disposition'))

                            if ctype == 'text/plain' and 'attachment' not in cdispo:
                                body = part.get_payload(decode = True)
                                break
                    else:
                        body = email_message.get_payload(decode = True)


                    parsed_body = body.decode("utf-8") 
                    parsed_body = parsed_body.replace("'", "")


                    try:
                        mycursor.execute("INSERT INTO `{}` (SENDER, SUBJECT, BODY) VALUES ('{}', '{}', '{}')".format(user, sender, subject, parsed_body[:255]))
                        mydb.commit()
                        print("Email Added Successfully!")
                    except:
                        print("Cannot Insert The Email Into The Table!")
                    

    print("Data Added To The Database!\n")


    try:
        mail.close()
    finally:
        mail.logout()



def read_csv():
    file = input("Enter The Filename: ").strip()

    try:
        with open(file, "r") as csv_file:
            reader = csv.reader(csv_file)

            for line in reader:
                user, password = line
                scrape(user, password)

    except:
        print("File Not Found!\n")




def show_table():
    table = input("Show The Following Table: ")

    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES")

    for x in mycursor:
        if x[0] == table:
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM `{}`".format(table))


            print("\nTABLE:\n")

            collumn_names = []
            for row in cursor.description:
                collumn_names.append(row[0].upper())
            
            print("")

            for i, row in enumerate(cursor):
                print(i)
                for index, element in enumerate(row):
                    print(collumn_names[index].upper(), ": ", element)

                print("")

            return
    
    print("Table Doesn't Exist!\n")




def main():

    while True:
        choice = None

        try:
            choice = int(input("1. Scrape Email Inbox\n2. Read Emails From File\n3. Show A Table\n9. Exit The Application\nChoice: "))
        except:
            print("Please Enter An Integer!\n")
            continue


        if choice == 1:
            user     = input("Email Address: ").strip()
            password = input("Password: ").strip()
            scrape(user, password)

        elif choice == 2:
            read_csv()
            
        elif choice == 3:
            show_table()

        elif choice == 9:
            print("Exiting The Application...\n")
            break

        else:
            print("Choice Not Found!\n")



if __name__ == "__main__":
    main()