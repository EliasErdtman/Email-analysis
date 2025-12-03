#!/usr/bin/env python3
"""
clean_inbox.py
Archive or delete emails older than N days that match a simple filter.
Usage:
python clean_inbox.py --user your-email@example.com --password app-password --days 30 --archive
"""
from email.mime.text import MIMEText
import imaplib, argparse, datetime, smtplib

# Gmail category filters
CATEGORIES = {
    "Promotions": "promotions",
    "Social": "social"
    #"Updates": "updates",
    #"Forums": "forums"
}

IMAP_SERVER = None
EMAIL_ACCOUNT = None
APP_PASSWORD = None
NOTIFY_EMAIL = None  # Set this to your notification email if needed
SMTP_SERVER = "smtp.gmail.com"

def delete_old_emails(cat, days):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    try:
        mail.select("INBOX")
        date_cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%d-%b-%Y")
        
        status, data_cat = mail.uid("search", None, f'X-GM-RAW "category:{cat}"') 
        if status != "OK":
            print(f"Search failed for category: {cat}")
            return 0
        
        status, data_time = mail.uid("search", None, f'BEFORE {date_cutoff}') 
        if status != "OK":
            print(f"Search failed for Time: {date_cutoff}")
            return 0
        
        mail_cat_ids = data_cat[0].split()
        mail_time_ids = data_time[0].split()
        mail_ids = list(set(mail_cat_ids) & set(mail_time_ids)) # intersection of both criteria
        deleted_count = len(mail_ids)
        print(f"Found {deleted_count} emails to delete in category {cat}.")
        for mail_id in mail_ids:
            mail.store(mail_id, '+FLAGS', '\\Deleted')
        mail.expunge()
        mail.close()
        mail.logout()
        return deleted_count
    except Exception as e:
        print(f"Error in category {cat}: {e}")
        return 0

def send_notification(results_dict):
    """Sends an email summarizing the cleanup."""
    if not NOTIFY_EMAIL:
        print("No NOTIFY_EMAIL set, skipping notification.")
        return
    body = "Gmail Cleanup Results:\n\n"
    for folder, count in results_dict.items():
        body += f"- {folder}: {count} deleted\n"
    msg = MIMEText(body)
    msg["Subject"] = "Gmail Cleanup Summary"
    msg["From"] = EMAIL_ACCOUNT
    msg["To"] = NOTIFY_EMAIL
    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
        server.login(EMAIL_ACCOUNT, APP_PASSWORD)
        server.sendmail(EMAIL_ACCOUNT, [NOTIFY_EMAIL], msg.as_string())

def main():
    global EMAIL_ACCOUNT, APP_PASSWORD, IMAP_SERVER, NOTIFY_EMAIL
    parser = argparse.ArgumentParser(description='Clean Gmail inbox by deleting or archiving old emails.')
    parser.add_argument('-u', '--user', required=True, help='Gmail address to connect with')
    parser.add_argument('-p', '--password', dest='password', required=True, help='Gmail app password')
    parser.add_argument('--imap', default='imap.gmail.com', help='IMAP server address')
    parser.add_argument('--days', type=int, default=30, help='Delete emails older than this many days')
    parser.add_argument('--notify', dest='notify_email', help='Email address to send summary notification to')
    args = parser.parse_args()
    EMAIL_ACCOUNT = args.user
    APP_PASSWORD = args.password
    IMAP_SERVER = args.imap
    NOTIFY_EMAIL = args.notify_email
    results = {}
    for name, cat in CATEGORIES.items():
        print(f"Cleaning category: {name}")
        deleted = delete_old_emails(cat, args.days)
        results[name] = deleted
    if NOTIFY_EMAIL:
        print("Sending summary email...")
        send_notification(results)
    print("Cleanup complete!")

if __name__ == "__main__":
    main()