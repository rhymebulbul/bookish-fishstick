import json
import smtplib
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# === Load credentials from config.json ===
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        SENDER_EMAIL = config["SENDER_EMAIL"]
        APP_PASSWORD = config["APP_PASSWORD"]
except FileNotFoundError:
    print("❌ config.json file not found. Please create it with your email and app password.")
    exit(1)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SUBJECT = "Software Engineering Opportunities at {company}"
RESUME_PATH = "data/Resume.pdf"

# === Email body template ===
EMAIL_TEMPLATE = """Hi {name},

I hope you're doing well!

I had the pleasure of attending the Monash University engineering networking event on July 25th, where I learned about the inspiring work happening at {company}. It left a strong impression, and I wanted to reach out personally.

I'm Rhyme, a Software Engineer with over three years of experience across fullstack and backend systems — primarily working with Java, Python, and Typescript — as well as cloud infrastructure and automation. I’m drawn to roles that blend engineering rigour with real-world impact, and I’d be genuinely excited to contribute to a team like yours.

I’ve attached my resume, and I’d really appreciate the opportunity to chat or be considered for any current or future roles that might be a fit. You can reach me by replying here or giving me a call on 0434 711 292 — I’d love to connect.

Warm regards,  
Rhyme Bulbul  
LinkedIn: https://www.linkedin.com/in/rhyme-bulbul/
"""

sent_emails = []
missing_emails = []

def extract_first_name(full_name):
    return full_name.split()[0] if full_name else "there"

def send_email(to_email, full_name, company):
    first_name = extract_first_name(full_name)

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = SUBJECT.format(company=company)

    # Add body
    body = EMAIL_TEMPLATE.format(name=first_name, company=company)
    msg.attach(MIMEText(body, 'plain'))

    # Attach resume
    try:
        with open(RESUME_PATH, 'rb') as f:
            resume = MIMEApplication(f.read(), _subtype='pdf')
            resume.add_header('Content-Disposition', 'attachment', filename='Rhyme_Bulbul_Resume.pdf')
            msg.attach(resume)
    except FileNotFoundError:
        print(f"❌ Resume not found at {RESUME_PATH}")
        return

    # Send email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            sent_emails.append((full_name, to_email, company))
            print(f"✅ Sent email to {full_name} at {to_email} ({company})")
    except Exception as e:
        print(f"❌ Failed to send to {to_email}: {e}")

# === Read CSV and send ===
def main():
    try:
        with open("data/contacts.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                email = row['email']
                company = row['company']

                if email.strip():
                    send_email(email.strip(), name.strip(), company.strip())
                else:
                    missing_emails.append((name.strip(), company.strip()))
    except FileNotFoundError:
        print("❌ contacts.csv file not found. Please ensure it exists in the current directory.")
        return

    # === Summary ===
    print("\n--- Summary ---")
    print(f"\n✅ Emails sent to:")
    for name, email, company in sent_emails:
        print(f"  - {name} ({email}) at {company}")

    print(f"\n🔗 No email found, reach out via LinkedIn:")
    for name, company in missing_emails:
        print(f"  - {name} at {company}")

if __name__ == "__main__":
    main()
