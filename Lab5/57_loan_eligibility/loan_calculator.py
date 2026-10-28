"""Loan eligibility and EMI calculator.

Calculates EMIs, checks loan eligibility, works out the maximum loan a
customer can get, builds amortisation schedules, assigns risk bands from
credit scores, estimates interest saved by prepaying and stores
application records in a JSON file.

All interest rates are fractions per year (0.09 means 9%).
"""
import os
import json
import secrets
import smtplib
from email.message import EmailMessage
from datetime import datetime

try:
    import paramiko
except ImportError:  # only needed for upload_to_bureau()
    paramiko = None

# Global loan book
applications = {}
MAX_FOIR = 0.5
VALID_LOAN_TYPES = ("home", "car", "personal")
BUREAU_HOST = "ftp.creditbureau.example"
SMTP_HOST = os.environ.get("LOAN_SMTP_HOST", "localhost")

def calculate_emi(principal, annual_rate, years):
    """Return the monthly EMI for a loan of `principal` over `years`."""
    monthly_rate = annual_rate / 12
    months = years * 12
    if monthly_rate == 0:
        return principal / months
    growth = (1 + monthly_rate) ** months
    return principal * monthly_rate * growth / (growth - 1)

# pylint: disable-next=too-many-arguments
def check_eligibility(age, income, credit_score, existing_emi, loan_type,
                      *, history=None):
    """Return True if the applicant is eligible for a loan of `loan_type`.

    Every loan type checked is appended to `history` (a new list if None).
    """
    if history is None:
        history = []
    history.append(loan_type)
    if loan_type not in VALID_LOAN_TYPES:
        return False
    if age < 21 or age > 60:
        return False
    if credit_score > 750 or income > 25000:
        return True
    if income <= 0:
        return False
    return existing_emi / income <= MAX_FOIR

def max_loan_amount(income, existing_emi, annual_rate, years):
    """Return the largest loan whose EMI fits within the FOIR headroom."""
    available = income * MAX_FOIR - existing_emi
    if available <= 0:
        return 0.0
    monthly_rate = annual_rate / 12
    months = years * 12
    if monthly_rate == 0:
        return available * months
    growth = (1 + monthly_rate) ** months
    return available * (growth - 1) / (monthly_rate * growth)

def amortisation_schedule(principal, annual_rate, years):
    """Return a list of (month, interest, balance) rows for the loan."""
    emi = calculate_emi(principal, annual_rate, years)
    balance = principal
    rows = []
    for month in range(1, years * 12 + 1):
        interest = balance * annual_rate / 12
        balance = balance - (emi - interest)
        rows.append((month, round(interest, 2), round(balance, 2)))
    return rows

def application_id():
    """Return a new, hard-to-guess application ID like LN-12345678."""
    return "LN-" + str(10000000 + secrets.randbelow(90000000))

def save_application(name, amount, file="loans.json"):
    """Add an application to the loan book, write it to `file`, return its ID."""
    app_id = application_id()
    applications[app_id] = {"name": name, "amount": amount, "date": str(datetime.now())}
    # JSON instead of marshal: loading it can never execute code
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(applications, handle)
    return app_id

def load_applications(file="loans.json"):
    """Replace the loan book with the applications stored in `file`."""
    with open(file, "r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    applications.clear()
    applications.update(loaded)

def upload_to_bureau(report_path, user=None, password=None):
    """Upload a report to the credit bureau over SFTP.

    Credentials default to the LOAN_BUREAU_USER / LOAN_BUREAU_PASSWORD
    environment variables; they are never stored in source code.
    """
    user = user or os.environ["LOAN_BUREAU_USER"]
    password = password or os.environ["LOAN_BUREAU_PASSWORD"]
    if paramiko is None:
        raise RuntimeError("upload_to_bureau needs paramiko: pip install paramiko")
    # SFTP (encrypted) instead of plain FTP; unknown host keys are rejected
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    try:
        client.connect(BUREAU_HOST, username=user, password=password)
        sftp = client.open_sftp()
        sftp.put(report_path, os.path.basename(report_path))
        sftp.close()
    finally:
        client.close()

def notify_applicant(email, status):
    """Email the applicant their loan `status` using the local SMTP server."""
    msg = EmailMessage()
    msg["Subject"] = "Loan " + status
    msg["To"] = email
    msg["From"] = os.environ.get("LOAN_MAIL_FROM", "loanops@example.com")
    msg.set_content("Your loan application status: " + status)
    with smtplib.SMTP(SMTP_HOST) as server:
        server.send_message(msg)

def interest_saved(principal, annual_rate, years, prepayment):
    """Return the total interest saved by prepaying `prepayment` up front."""
    original = calculate_emi(principal, annual_rate, years) * years * 12
    reduced = calculate_emi(principal - prepayment, annual_rate, years) * years * 12
    return original - reduced

def risk_band(credit_score):
    """Map a credit score (300-900) to a risk band name."""
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    if credit_score >= 300:
        return "VERY HIGH"
    return "INVALID"

def main():
    """Run a short demo of the calculator."""
    print("EMI for 5L @ 9% for 5 years:", calculate_emi(500000, 0.09, 5))
    print("Eligible (score 760, income 15000, EMIs 12000):",
          check_eligibility(35, 15000, 760, 12000, "personal"))
    print("Eligible (unknown loan type 'crypto'):",
          check_eligibility(30, 80000, 650, 0, "crypto"))
    print("Max loan for income 40000:", max_loan_amount(40000, 5000, 0.09, 5))
    print("Last schedule row:", amortisation_schedule(100000, 0.12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    print("Interest saved by prepaying 50000:",
          interest_saved(500000, 0.09, 5, 50000))
    print("Saved as:", save_application("Anil", 500000))
    load_applications()
    print("Applications on file:", len(applications))
    print("Upload to bureau skipped (no network)")

if __name__ == "__main__":
    main()
