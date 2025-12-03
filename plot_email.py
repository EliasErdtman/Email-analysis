import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "email_log.csv"

# ----------------------------------------------------------
# Load data
# ----------------------------------------------------------
df = pd.read_csv(CSV_FILE, parse_dates=["date"])

# Ensure category exists (fallback to unknown)
#df["category"] = df["category"].fillna("Unknown")

# ----------------------------------------------------------
# 1. EMAILS PER MONTH
# ----------------------------------------------------------
df["year_month"] = df["date"].dt.to_period("M")

emails_per_month = df.groupby("year_month").size()

plt.figure(figsize=(10, 5))
emails_per_month.plot(kind="bar")
plt.title("Emails per Month")
plt.xlabel("Month")
plt.ylabel("Number of Emails")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# 2. EMAILS PER WEEKDAY
# ----------------------------------------------------------
df["weekday"] = df["date"].dt.day_name()

emails_per_weekday = df["weekday"].value_counts().reindex([
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
])

plt.figure(figsize=(10, 5))
emails_per_weekday.plot(kind="bar")
plt.title("Emails per Weekday")
plt.xlabel("Weekday")
plt.ylabel("Number of Emails")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# 3. TOP 10 SENDERS BY CATEGORY
# ----------------------------------------------------------
top_senders = (
    df.groupby(["category", "sender"])
      .size()
      .reset_index(name="count")
)

# Sort by count and keep only the top 10
top10 = top_senders.sort_values("count", ascending=False).head(10)

# Create a readable sender+category label
top10["label"] = top10["sender"] + " (" + top10["category"] + ")"

plt.figure(figsize=(12, 6))
plt.bar(top10["label"], top10["count"])
plt.title("Top 10 Most Frequent Senders (with Category)")
plt.xlabel("Sender + Category")
plt.ylabel("Email Count")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()