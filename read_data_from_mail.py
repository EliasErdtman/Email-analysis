import imaplib
import email
from email.utils import parsedate_to_datetime
from email.header import decode_header
import pandas as pd
import os
import re
import argparse

IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = None
EMAIL_PASS = None  # Will be provided via command-line arguments
CSV_FILE = "email_log.csv"
UID_CACHE_FILE = "processed_uids.txt"

CATEGORIES = {
	#"Primary": "primary",
    "Promotions": "promotions",
    "Social": "social"
    #"Updates": "Updates",
    #"Forums": "forums"
}

# ----------------------------
# Utility helpers
# ----------------------------

def decode_mime_header(raw):
	"""Decode MIME-encoded email headers (RFC 2047)."""
	if not raw:
		return ""
	parts = decode_header(raw)
	decoded = ""
	for text, enc in parts:
		if isinstance(text, bytes):
			decoded += text.decode(enc or "utf-8", errors="ignore")
		else:
			decoded += text
	return decoded

def clean_sender(raw_sender):
	"""Clean sender by decoding MIME, removing quotes, and stripping email."""
	if not raw_sender:
		return ""

	# Decode UTF-8, Base64, Quoted-Printable headers etc.
	sender = decode_mime_header(raw_sender).strip()
	
	if sender is None:
		return ""
	sender = sender.replace('"', "").strip()
	if "<" in sender:
		return sender.split("<")[0].strip()
	return sender
	
def clean_sender_email(sender_raw):
	"""Extract a clean sender email address."""
	if not sender_raw:
		return "Unknown"
	match = re.search(r'[\w\.-]+@[\w\.-]+', sender_raw)
	return match.group(0) if match else sender_raw


def load_uid_cache():
	if not os.path.exists(UID_CACHE_FILE):
		return set()
	with open(UID_CACHE_FILE, "r") as f:
		return set(line.strip() for line in f)


def save_uid_cache(uids):
	with open(UID_CACHE_FILE, "w") as f:
		for uid in uids:
			f.write(uid + "\n")


# ----------------------------
# Main email processing function
# ----------------------------

def fetch_gmail_headers(cat):
	print("Connecting to Gmail…")
	imap = imaplib.IMAP4_SSL(IMAP_SERVER)
	imap.login(EMAIL_USER, EMAIL_PASS)

	# Always search in INBOX — categories can be filtered with X-GM-RAW
	imap.select("INBOX")

	# Fetch UIDs
	#for cat in cat = 'social'#'promotions'
	status, data = imap.uid("search", None, f'X-GM-RAW "category:{cat}"')
	all_uids = data[0].split()

	if not all_uids:
		print("No emails found.")
		return pd.DataFrame([])

	print(f"Total emails in category {cat}: {len(all_uids)}")

	# Load previously processed UIDs
	processed = load_uid_cache()
	new_uids = [uid for uid in all_uids if uid.decode() not in processed]

	print(f"New emails to process: {len(new_uids)}")

	if not new_uids:
		print("No new emails. Done.")
		return pd.DataFrame([])

	# Batch fetch
	uid_range = ",".join(uid.decode() for uid in new_uids)
	status, fetch_data = imap.uid(
		"fetch",
		uid_range,
		'(BODY.PEEK[HEADER.FIELDS (DATE FROM)])'
	)
	print(len(fetch_data))

	records = []
	current_uid = None

	for entry in fetch_data:
		if isinstance(entry, tuple):
			# Extract UID from metadata
			header = entry[0].decode()
			parts = header.split()
			for p in parts:
				p = p.replace(')','')
				p = p.replace('(','')
				
				if p.startswith("UID"):
					if p.strip(): # Check if p contains non-whitespace characters
						current_uid = parts[2] if len(parts) > 2 else None
					else:
						current_uid = None
					
			raw = entry[1].decode(errors="ignore")
			lines = raw.splitlines()

			date_raw = None
			from_raw = None

			for line in lines:
				line_low = line.lower()
				if line_low.startswith("date:"):
					date_raw = line[5:].strip()
				elif line_low.startswith("from:"):
					from_raw = line[5:].strip()

			if not date_raw:
				continue

			try:
				date_obj = pd.to_datetime(parsedate_to_datetime(date_raw),utc=True, format="%Y-%m-%d %H:%M:%S%z")
			except:
				continue
			#print(from_raw)
			sender = clean_sender(from_raw)
			#print(sender)
			records.append({
				"uid": current_uid,
				"date": date_obj,
				"sender": sender,
				"category": cat
			})

	imap.logout()
	return pd.DataFrame(records)


# ----------------------------
# Save to CSV (with incremental updates)
# ----------------------------

def save_to_csv(new_records: pd.DataFrame):
	if new_records.empty:
		return
	new_records["date"] = pd.to_datetime(new_records["date"])
	# Load existing CSV if it exists
	if os.path.exists(CSV_FILE):
		old_df = pd.read_csv(CSV_FILE, parse_dates=["date"])
		combined = pd.concat([old_df, new_records], ignore_index=True)
	else:
		combined = new_records

	combined.drop_duplicates(subset="uid", inplace=True)
	combined.to_csv(CSV_FILE, index=False)
	print(f"Saved {len(combined)} records to {CSV_FILE}")


# ----------------------------
# Run everything
# ----------------------------

def main():
    # Parse command-line arguments for email and password
    parser = argparse.ArgumentParser(description='Fetch Gmail headers and store to CSV.')
    parser.add_argument('-u', '--user', required=True, help='Gmail address to connect with')
    parser.add_argument('-p', '--password', dest='password', required=True, help='Gmail app password')
    args = parser.parse_args()

    global EMAIL_USER, EMAIL_PASS
    EMAIL_USER = args.user
    EMAIL_PASS = args.password

    df_new = pd.DataFrame([])
    for name, cat in CATEGORIES.items():
        print(f'Extracting from {name}')
        df_new = pd.concat([df_new, fetch_gmail_headers(cat)], ignore_index=True)

    if df_new.empty:
        print("Nothing to update.")
        return
    
    total_elements = df_new.size
    # Update CSV
    #print(df_new.head())
    save_to_csv(df_new)

    # Update UID cache
    processed = load_uid_cache()
    new_uids = set(df_new["uid"].astype(str).tolist())
    save_uid_cache(processed.union(new_uids))

    print("Done.")


if __name__ == "__main__":
    main()
