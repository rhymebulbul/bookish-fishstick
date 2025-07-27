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

I recently attended the industry networking event at Monash University on July 25th hosted by the Faculty of Engineering, where I had the chance to learn more about the exciting work happening at {company}. The insights I gained reaffirmed my interest in contributing to innovative, impactful engineering teams like yours.

I’m a Software Engineer with hands-on experience in cloud platforms, infrastructure automation, fullstack and backend systems using Java, Python & Javascript/Typescript. I’m especially drawn to environments where I can grow technically while contributing to real-world solutions — something I believe your team exemplifies.

Please find my resume attached. I’d be genuinely grateful for a chance to connect or to be considered for any opportunities you think might align.

Kind regards,  
Rhyme Bulbul  
LinkedIn: https://www.linkedin.com/in/rhyme-bulbul/
"""


sent_emails = []
missing_emails = []

def send_email(to_email, to_name, company):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = SUBJECT.format(company=company)

    # Add body
    body = EMAIL_TEMPLATE.format(name=to_name, company=company)
    msg.attach(MIMEText(body, 'plain'))

    # Attach resume
    try:
        with open(RESUME_PATH, 'rb') as f:
            resume = MIMEApplication(f.read(), _subtype='docx')
            resume.add_header('Content-Disposition', 'attachment', filename='Rhyme_Bulbul_Resume.docx')
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
            sent_emails.append((to_name, to_email, company))
            print(f"✅ Sent email to {to_name} at {to_email} ({company})")
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