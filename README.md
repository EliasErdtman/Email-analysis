# Email Analysis Suite

A collection of Python scripts for analyzing and managing Gmail emails programmatically.

## Files

### `read_data_from_mail.py`
Fetches email headers from Gmail categories and stores them in a CSV file for analysis.

**Features:**
- Connects to Gmail via IMAP
- Fetches emails from specified categories (Promotions, Social, etc.)
- Extracts date, sender, and category information
- Caches processed UIDs to avoid re-processing
- Saves data incrementally to CSV

**Usage:**
```powershell
python .\read_data_from_mail.py --user your-email@gmail.com --password your-app-password
```

**Arguments:**
- `-u, --user` (required): Gmail address to connect with
- `-p, --password` (required): Gmail app password

**Output:**
- `email_log.csv`: Contains all fetched emails (date, sender, category, UID)
- `processed_uids.txt`: Cache of already-processed email UIDs

---

### `clean_inbox.py`
Cleans up old emails from Gmail folders by deleting them and optionally sending a summary notification.

**Features:**
- Connects to Gmail via IMAP
- Searches for emails older than N days in specified folders
- Deletes old emails and removes them permanently
- Optionally sends a summary email of cleanup results
- Works on multiple Gmail categories (Promotions, Social, Updates, Forums)

**Usage:**
```powershell
python .\clean_inbox.py --user your-email@gmail.com --password your-app-password --days 30
```

**Arguments:**
- `-u, --user` (required): Gmail address to connect with
- `-p, --password` (required): Gmail app password
- `--days` (optional): Delete emails older than this many days (default: 30)
- `--imap` (optional): IMAP server address (default: imap.gmail.com)
- `--notify` (optional): Email address to send cleanup summary to

**Example:**
```powershell
python .\clean_inbox.py --user you@gmail.com --password app-pass --days 60 --notify admin@example.com
```

---

### `plot_email.py`
Visualizes email data from the CSV log (implementation details depend on your specific needs).

---

## Data Files

- **email_log.csv**: CSV file containing fetched email records with columns: uid, date, sender, category
- **processed_uids.txt**: Text file with one UID per line, tracking which emails have been processed

---

## Setup

### Prerequisites
- Python 3.7+
- pandas
- imaplib (built-in)
- argparse (built-in)

### Gmail Configuration
1. Create a [Gmail App Password](https://support.google.com/accounts/answer/185833) (not your regular Gmail password)
2. Enable IMAP in Gmail settings
3. Use the app password with these scripts

### Install Dependencies
```powershell
pip install pandas
```

---

## Security Notes

⚠️ **Important:** Never hardcode credentials in scripts. Always use command-line arguments as provided.

For production use, consider:
- Using environment variables for sensitive data
- Storing credentials in a secure config file with restricted permissions
- Using OS credential managers

---

## Example Workflow

1. **Fetch new emails:**
   ```powershell
   python .\read_data_from_mail.py --user you@gmail.com --password your-app-password
   ```

2. **Analyze the data:**
   ```powershell
   python .\plot_email.py
   ```

3. **Clean up old emails:**
   ```powershell
   python .\clean_inbox.py --user you@gmail.com --password your-app-password --notify admin@example.com --days 60
   ```

---

## Troubleshooting

- **"Could not access folder"**: Ensure IMAP is enabled in Gmail settings
- **Authentication failed**: Verify your email and app password are correct
- **No emails found**: Check that the category filters match your Gmail labels

---

## License

Use at your own discretion.
