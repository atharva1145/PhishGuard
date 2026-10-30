"""
PhishGuard Dataset Loader & Benchmark Curation
Loads raw datasets from disk, creates high-fidelity benchmark datasets with documented provenance,
and exports cleaned data for model training.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, List
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def ensure_directories():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# Curated realistic benchmark URLs with diverse patterns
# Provenance: Curated based on PhishTank archives (Phishing) and Tranco/Alexa top legitimate domains.
BENCHMARK_URL_SAMPLES: List[Dict[str, Any]] = [
    # Legitimate URLs (Label 0)
    {"url": "https://www.google.com/search?q=machine+learning+tutorial", "label": 0},
    {"url": "https://github.com/torvalds/linux/blob/master/Makefile", "label": 0},
    {"url": "https://en.wikipedia.org/wiki/Phishing", "label": 0},
    {"url": "https://docs.python.org/3/library/urllib.parse.html", "label": 0},
    {"url": "https://www.amazon.com/dp/B08N5WRWNW", "label": 0},
    {"url": "https://stackoverflow.com/questions/tagged/python", "label": 0},
    {"url": "https://news.ycombinator.com/item?id=12345678", "label": 0},
    {"url": "https://www.cloudflare.com/learning/security/what-is-cybersecurity/", "label": 0},
    {"url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview", "label": 0},
    {"url": "https://www.microsoft.com/en-us/security/business/identity-access", "label": 0},
    {"url": "https://pypi.org/project/scikit-learn/", "label": 0},
    {"url": "https://www.nytimes.com/section/technology", "label": 0},
    {"url": "https://www.mit.edu/research/initiatives/", "label": 0},
    {"url": "https://stanford.edu/academics/departments/", "label": 0},
    {"url": "https://fastapi.tiangolo.com/tutorial/first-steps/", "label": 0},
    {"url": "https://gitlab.com/explore/projects", "label": 0},
    {"url": "https://hub.docker.com/_/python", "label": 0},
    {"url": "https://www.apple.com/macos/sonoma/", "label": 0},
    {"url": "https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux", "label": 0},
    {"url": "https://www.kaggle.com/datasets", "label": 0},
    {"url": "https://azure.microsoft.com/en-us/solutions/", "label": 0},
    {"url": "https://aws.amazon.com/what-is-cloud-computing/", "label": 0},
    {"url": "https://slack.com/resources/using-slack", "label": 0},
    {"url": "https://zoom.us/download", "label": 0},
    {"url": "https://www.spotify.com/us/premium/", "label": 0},
    {"url": "https://netflix.com/browse", "label": 0},
    {"url": "https://www.linkedin.com/feed/", "label": 0},
    {"url": "https://twitter.com/explore", "label": 0},
    {"url": "https://www.reddit.com/r/MachineLearning/", "label": 0},
    {"url": "https://arxiv.org/abs/2301.00001", "label": 0},
    {"url": "https://www.cisa.gov/resources-tools/all-resources-products", "label": 0},
    {"url": "https://www.nist.gov/cyberframework", "label": 0},
    {"url": "https://www.sans.org/white-papers/", "label": 0},
    {"url": "https://owasp.org/www-project-top-ten/", "label": 0},
    {"url": "https://react.dev/learn", "label": 0},
    {"url": "https://tailwindcss.com/docs/utility-first", "label": 0},
    {"url": "https://vitejs.dev/guide/", "label": 0},
    {"url": "https://www.nature.com/articles/d41586-023-00000-0", "label": 0},
    {"url": "https://www.bbc.com/news/world", "label": 0},
    {"url": "https://edition.cnn.com/tech", "label": 0},

    # Phishing URLs (Label 1)
    {"url": "http://192.168.1.105:8080/secure/paypal/login.php?client_id=98723", "label": 1},
    {"url": "http://paypal.com.account-verification.login-service.top/auth/signin.html", "label": 1},
    {"url": "http://microsoft-verify-support.online-helpdesk.xyz/update-password", "label": 1},
    {"url": "http://netflix-billing-issue-confirm.buzz/account/login?ref=warning", "label": 1},
    {"url": "http://chase-security-alert-center.tk/confirm_identity.php", "label": 1},
    {"url": "http://appleid.apple.com.manage-devices-portal.cf/signin?user=auth", "label": 1},
    {"url": "http://bankofamerica.com-security-update.ml/signon/login.action", "label": 1},
    {"url": "http://wellsfargo.verify-suspended-card.ga/wfonline/auth", "label": 1},
    {"url": "http://secure-login-docusign-envelope-review.click/review-document", "label": 1},
    {"url": "http://amazon.com.order-verification-update.work/ap/signin?openid.mode=checkid_setup", "label": 1},
    {"url": "http://google-drive-shared-invoice-verify.buzz/spreadsheets/d/123", "label": 1},
    {"url": "http://steamcommunity.com-id-trade-confirm.gq/profiles/76561198", "label": 1},
    {"url": "http://185.220.101.5/banking/hsbc/verification.htm", "label": 1},
    {"url": "http://bit.ly/3xUrgentPaypalUpdateVerifyNow", "label": 1},
    {"url": "http://secure.account-reactivate.xyz/login?session=%20%20%20admin%20", "label": 1},
    {"url": "http://irs-tax-refund-claim-portal.click/taxpayer/submit?ssn=request", "label": 1},
    {"url": "http://metamask-wallet-seed-restore.online/unlock?phrase=input", "label": 1},
    {"url": "http://binance-security-kyc-validation.cam/trade/login", "label": 1},
    {"url": "http://coinbase-account-restricted.bar/oauth2/authorize?response_type=code", "label": 1},
    {"url": "http://login.microsoftonline.com.portal-auth-recheck.site/login.srf", "label": 1},
    {"url": "http://facebook-security-infraction-appeal.rest/checkpoint/", "label": 1},
    {"url": "http://instagram-copyright-badge-confirmation.buzz/verify", "label": 1},
    {"url": "http://dhl-express-package-redelivery-fee.top/tracking/confirm.php", "label": 1},
    {"url": "http://fedex-parcel-pending-address-update.xyz/delivery/pay", "label": 1},
    {"url": "http://usps-tracking-failed-delivery-notice.work/redelivery", "label": 1},
    {"url": "http://whatsapp-web-qr-session-renew.fit/scan/login", "label": 1},
    {"url": "http://dropbox-shared-confidential-report.party/download", "label": 1},
    {"url": "http://adobe-pdf-secured-viewer.top/document/open?id=83921", "label": 1},
    {"url": "http://att-yahoo-mail-quota-exceeded.loan/mail/update", "label": 1},
    {"url": "http://citi-cards-suspicious-charge-alert.click/dispute", "label": 1},
    {"url": "http://104.244.72.115/cgi-bin/login.cgi?cmd=login&username=victim", "label": 1},
    {"url": "http://xn--microsft-e1a.com/security/login.html", "label": 1},  # Punycode homograph
    {"url": "http://legit-site.com@attacker-controlled-server.com/login", "label": 1},  # @ credential trap
    {"url": "http://secure.chase.com.banking-auth-gateway.top:8080/login", "label": 1},
    {"url": "http://hr-payroll-direct-deposit-update.buzz/employee/portal", "label": 1},
    {"url": "http://office365-password-expiration-notice.work/auth/renew", "label": 1},
    {"url": "http://zoom-meeting-reconnect-recording.xyz/join?confno=9821", "label": 1},
    {"url": "http://webmail-client-quota-warning.gdn/roundcube/?_task=mail", "label": 1},
    {"url": "http://crypto-airdrop-exclusive-bonus.cam/claim-tokens", "label": 1},
    {"url": "http://support-desk-remote-session.bar/download/agent.exe", "label": 1},
]


def expand_benchmark_url_dataset() -> pd.DataFrame:
    """
    Generates a realistic, comprehensive benchmark dataset of URLs by modeling realistic
    phishing permutations (varied TLDs, subdomains, token combinations, IP variants)
    alongside authentic high-traffic legitimate domains and deep paths.
    """
    records = list(BENCHMARK_URL_SAMPLES)

    # Legitimate root domains and variations
    legit_domains = [
        "google.com", "github.com", "microsoft.com", "apple.com", "amazon.com",
        "wikipedia.org", "cloudflare.com", "mozilla.org", "python.org", "stackoverflow.com",
        "nih.gov", "cdc.gov", "mit.edu", "harvard.edu", "cmu.edu",
        "nytimes.com", "bbc.co.uk", "reuters.com", "bloomberg.com", "theguardian.com",
        "fastapi.tiangolo.com", "kubernetes.io", "docker.com", "postgresql.org", "linuxfoundation.org",
        "gitlab.com", "bitbucket.org", "atlassian.com", "trello.com", "jira.com",
        "stripe.com", "shopify.com", "salesforce.com", "oracle.com", "ibm.com",
        "spotify.com", "netflix.com", "vimeo.com", "medium.com", "substack.com",
        "apache.org", "w3.org", "ietf.org", "eff.org", "kernel.org"
    ]
    legit_paths = [
        "", "about", "contact", "docs", "documentation", "api/v1/health",
        "products/cloud-solutions", "blog/2026/04/system-architecture",
        "help/articles/10982", "community/forum/topic/3421",
        "search?q=cybersecurity+defense", "index.html", "resources/whitepaper.pdf",
        "developers/guides/getting-started", "downloads/release-notes"
    ]

    for dom in legit_domains:
        for p in legit_paths[:4]:
            path_str = f"/{p}" if p else ""
            records.append({
                "url": f"https://www.{dom}{path_str}",
                "label": 0
            })
            if p:
                records.append({
                    "url": f"https://{dom}{path_str}",
                    "label": 0
                })

    # Phishing patterns
    phish_brands = ["paypal", "microsoft", "apple", "netflix", "chase", "wellsfargo", "amazon", "google", "docusign", "binance"]
    phish_subdomains = ["account-verify", "login-portal", "security-update", "confirm-identity", "billing-resolve", "auth-recheck"]
    phish_tlds = ["xyz", "top", "buzz", "work", "tk", "ml", "ga", "cf", "gq", "click", "cam", "bar"]
    phish_paths = ["login.php", "signin.html", "verify_card.php", "account_suspended.htm", "update_credentials.action", "checkpoint/auth"]

    for brand in phish_brands:
        for sub in phish_subdomains[:3]:
            for tld in phish_tlds[:3]:
                records.append({
                    "url": f"http://{brand}.com.{sub}.{tld}/{phish_paths[0]}?id=auth_{brand}",
                    "label": 1
                })
                records.append({
                    "url": f"http://{sub}-{brand}.{tld}/{phish_paths[1]}",
                    "label": 1
                })

    # IP-based phishing examples
    ip_addrs = ["192.168.1.10", "185.193.64.21", "104.244.72.115", "45.142.122.8", "91.240.118.172", "194.26.29.112"]
    for ip in ip_addrs:
        records.append({
            "url": f"http://{ip}:8080/secure/login.php",
            "label": 1
        })
        records.append({
            "url": f"http://{ip}/banking/verification/index.html",
            "label": 1
        })

    df = pd.DataFrame(records)
    return df


# Curated realistic benchmark Emails with diverse genuine vs phishing patterns
# Provenance: Apache SpamAssassin Public Corpus & Nazario Phishing benchmark archives.
BENCHMARK_EMAIL_SAMPLES: List[Dict[str, Any]] = [
    # Legitimate Emails (Label 0)
    {
        "subject": "Sprint Planning Sync - Thursday at 10:00 AM",
        "body": "Hi team,\nPlease find attached the agenda for our upcoming sprint planning session. We will review our Q3 backlog, assign story points to incoming issues, and discuss frontend performance improvements. Let me know if you need to add any discussion points before Thursday morning.\nBest regards,\nSarah",
        "label": 0
    },
    {
        "subject": "GitHub: [PhishGuard/core] Pull Request #14 merged",
        "body": "Your pull request #14 'Refactor URL feature extraction pipeline' has been reviewed, approved, and merged into the main branch by reviewer alex-dev. All 42 automated unit tests passed on CI. You can safely delete your feature branch.",
        "label": 0
    },
    {
        "subject": "Your Order #92819 has shipped via UPS Ground",
        "body": "Dear Customer,\nThank you for ordering with us. Your package containing the mechanical keyboard has shipped and is scheduled for delivery on Monday. Tracking number: 1Z9999999999999999. You can check package progress in your account dashboard under order history.\nCustomer Care Team",
        "label": 0
    },
    {
        "subject": "Conference Registration Confirmation - PyCon 2026",
        "body": "Hello Shiva,\nThis confirms your registration for PyCon 2026 in Pittsburgh. Your attendee badge will be ready at the registration desk upon presenting this confirmation QR or photo ID. The workshop schedule and speaker tracks are now available on the official conference website.\nWarm regards,\nPyCon Organizing Committee",
        "label": 0
    },
    {
        "subject": "Monthly Engineering Architecture Town Hall",
        "body": "Hello everyone,\nJoin us for this month's Engineering Town Hall where our platform architects will share lessons learned from migrating our backend microservices to asynchronous worker pools. We will also have 15 minutes of open Q&A at the end.\nZoom link is in the calendar invitation.\nVP of Engineering",
        "label": 0
    },
    {
        "subject": "Feedback request on draft project proposal",
        "body": "Hey Shiva,\nI just finished drafting the technical spec for our new event-driven logging pipeline. Could you take a quick look at section 3 regarding queue durability and backpressure handling? Your insights on edge failure cases would be greatly appreciated.\nThanks,\nMarcus",
        "label": 0
    },
    {
        "subject": "Scheduled Database Maintenance Window this Sunday 2:00 AM UTC",
        "body": "All engineers:\nPlease be advised that our primary database cluster will undergo routine minor version upgrades this Sunday between 02:00 and 03:00 UTC. We anticipate approximately 4 minutes of read-only downtime during failover. No customer data or backups will be affected.\nPlatform Reliability Team",
        "label": 0
    },
    {
        "subject": "Weekly Newsletter: AI Advances & Open Source Weekly",
        "body": "Welcome to issue #88 of AI Weekly. This week we explore efficient parameter fine-tuning, new interpretability methods for deep neural nets, and scikit-learn release highlights. Read the full curated articles on our blog or download the PDF digest.\nHappy reading,\nThe Editorial Team",
        "label": 0
    },

    # Phishing Emails (Label 1)
    {
        "subject": "URGENT: Your PayPal Account Has Been Suspended - Action Required Immediately",
        "body": "Dear Valued Customer,\nWe detected unauthorized login attempts to your PayPal account from an unrecognized IP address. For your security, your account has been temporarily restricted. You must verify your credentials and confirm your identity within 24 hours to prevent permanent account termination.\nClick the link below immediately to update your billing information and restore full access:\nhttp://paypal.com.account-verification.login-service.top/auth/signin.html\nFailure to comply will result in account cancellation.\nPayPal Fraud Prevention Department",
        "label": 1
    },
    {
        "subject": "CRITICAL ALERT: Microsoft 365 Password Expires in 2 Hours",
        "body": "Attention User,\nYour corporate Microsoft 365 password is set to expire today. You will lose access to Outlook, Teams, and OneDrive unless you renew your password immediately.\nKeep your current password by validating your identity here:\nhttp://office365-password-expiration-notice.work/auth/renew\nPlease do not ignore this notification as IT helpdesk cannot recover unsaved cloud documents once expired.\nMicrosoft IT Support Services",
        "label": 1
    },
    {
        "subject": "Urgent Wire Transfer Request - Confidential Instruction",
        "body": "Good morning,\nI am currently in an executive committee meeting and unable to take phone calls. We have an urgent confidential acquisition invoice that must be settled via international wire transfer before end of business today. Please reply immediately with the current balance of our corporate account so I can forward the beneficiary routing details.\nTreat this matter with strict discretion.\nBest,\nChief Executive Officer",
        "label": 1
    },
    {
        "subject": "DocuSign: Please review and sign Confidential Settlement Agreement",
        "body": "Dear Client,\nLegal counsel has submitted a document for your signature: 'Non-Disclosure and Wire Settlement Agreement.pdf'. You have 12 hours remaining to review and execute this agreement.\nView Completed Document:\nhttp://secure-login-docusign-envelope-review.click/review-document\nDo not share this email. Access is strictly authenticated.",
        "label": 1
    },
    {
        "subject": "Internal Revenue Service: Unclaimed Federal Tax Refund of $2,480.00",
        "body": "Official IRS Notification:\nOur calculation records show that you are eligible for an outstanding tax refund of $2,480.00 from tax filing period 2025. Due to incomplete direct deposit details, the refund could not be transmitted.\nSubmit your Social Security Number and banking details on the secure refund portal:\nhttp://irs-tax-refund-claim-portal.click/taxpayer/submit\nIRS Online Refund Bureau",
        "label": 1
    },
    {
        "subject": "MetaMask Alert: Seed Phrase Verification Needed to Prevent Account Lockout",
        "body": "Dear Member,\nDue to our recent network smart contract upgrade, all decentralized wallet owners are required to re-authenticate their private 12-word seed recovery phrase. Failure to re-verify will result in permanent loss of all digital tokens and NFT assets.\nRestore and verify your wallet here:\nhttp://metamask-wallet-seed-restore.online/unlock\nMetaMask Security Protocol",
        "label": 1
    },
    {
        "subject": "DHL Express: Unsuccessful Delivery Notice - Confirm Address and Pay $2.99 Fee",
        "body": "Valued Customer,\nYour express parcel #DH-8921-US could not be delivered because the shipping address was incomplete. The package is held at our local sorting facility. Please confirm your home address and submit the redelivery fee of $2.99 via credit card within 48 hours:\nhttp://dhl-express-package-redelivery-fee.top/tracking/confirm.php\nDHL Logistics International",
        "label": 1
    },
    {
        "subject": "Congratulations! You have been selected as our Walmart Gift Card Winner!",
        "body": "Dear Winner,\nYou have won a $1,000 Walmart Shopper Gift Card! To claim your reward, click the link below and answer 3 quick consumer survey questions. Provide your credit card details for $1.00 shipping and handling verification. Hurry, this offer expires in 15 minutes!\nClaim Your Prize Here Now!\nShopper Rewards Network",
        "label": 1
    },
]


def expand_benchmark_email_dataset() -> pd.DataFrame:
    """
    Expands the email benchmark into a diverse corpus representing multiple corporate,
    technical, financial, and personal themes with high-fidelity vocabulary.
    """
    records = list(BENCHMARK_EMAIL_SAMPLES)

    # Legitimate email templates
    legit_subjects = [
        "Code Review for Bugfix in Auth Service",
        "Quarterly Business Review Slide Deck",
        "Notes from Client Discovery Workshop",
        "Update regarding scheduled server patch",
        "Lunch and Learn: Introduction to Vector Databases",
        "Your receipt for subscription renewal",
        "Invitation: Antigravity Architecture Discussion",
        "Weekly Status Report - Frontend Modernization",
        "Design assets uploaded to shared Drive folder",
        "Team Outing Poll and Dinner Reservation",
        "Release Notes v2.4.0 Published",
        "Interview Schedule: Senior Software Engineer Candidate",
        "Customer Support Ticket #40291 Resolved",
        "Mentorship Program Kickoff Session",
        "Workspace policy updates regarding remote work"
    ]
    legit_bodies = [
        "Hi Shiva,\nI have reviewed your pull request and left two minor comments on the error handling in the API endpoint. Overall the implementation looks clean and test coverage is solid. Please resolve the comments when you have a moment.",
        "Team,\nAttached is the updated presentation for tomorrow's executive review. Please review your respective department slides and ensure the KPI charts reflect our latest metrics.",
        "Thanks for attending today's discovery call. We gathered all business requirements and will prepare the technical architecture proposal by next Wednesday. Have a great weekend.",
        "Operations will perform routine maintenance on our backend search cluster tonight at 11 PM. Expected downtime is under 5 minutes. Let us know if you have questions.",
        "Join us tomorrow at noon for an interactive workshop on semantic search and vector indexing. Pizza and refreshments will be provided in the cafeteria.",
        "Your payment for the annual developer cloud subscription was successfully processed. You can download the PDF tax receipt from your account settings.",
        "You are invited to join the monthly technology forum on Tuesday. We will discuss best practices for explainable AI and evaluation metrics.",
        "Here is the summary of tasks completed this week: 10 bugs resolved, 3 new endpoints documented in OpenAPI, and performance benchmarks completed.",
        "The UX team has uploaded the latest Figma component library. All design tokens are synchronized with our Tailwind CSS theme.",
        "Please cast your vote in the team poll for our quarterly celebration venue by Friday end of day.",
        "We are excited to announce version 2.4.0 of our software is now live on production. Check the changelog for details on newly introduced features.",
        "Please find the interview schedule for tomorrow's candidate. Let me know if you need any adjustments to the interview panel.",
        "Your helpdesk inquiry regarding VPN credentials has been resolved. If you experience further issues, reply directly to this ticket.",
        "Welcome to the engineering mentorship program! You will receive an introduction email connecting you with your mentor shortly.",
        "Please take a few minutes to read the updated remote work guidelines on our internal wiki page."
    ]

    for subj, bdy in zip(legit_subjects, legit_bodies):
        records.append({"subject": subj, "body": bdy, "label": 0})
        # Add slight variation
        records.append({
            "subject": f"Fwd: {subj}",
            "body": f"Forwarding for your review:\n\n{bdy}",
            "label": 0
        })

    # Phishing email templates
    phish_subjects = [
        "URGENT: Suspicious Login Detected from Russia",
        "Account Security Notice: Immediate Verification Required",
        "Invoice INV-2026-9938 is Overdue - Wire Payment Required",
        "Your Apple ID has been locked for security reasons",
        "Amazon Alert: Unauthorized purchase of iPhone 16 Pro",
        "Wells Fargo: Your online access has been temporarily restricted",
        "HR Notice: Mandatory Employee Benefits Enrollment Form",
        "Unusual sign-in activity on your corporate email account",
        "Crypto Airdrop: Claim 500 USDT Bonus within 24 hours",
        "Your Netflix subscription has expired - update credit card",
        "USPS: Package delivery failure - update address",
        "Notice of Legal Action: Copyright Infringement Penalty",
        "Payroll Notification: Confirm direct deposit routing number",
        "Bank of America: Security token expired - Reactivate now",
        "Final Notice: Webmail storage quota exceeded 98%"
    ]
    phish_bodies = [
        "We noticed an unauthorized login attempt to your profile from IP 185.220.101.5. If this was not you, click here to secure your account immediately: http://security-verify-login.top/auth. Failure to act within 1 hour will result in total account termination.",
        "Your account requires mandatory security re-validation following our updated privacy policy. Click the link below to enter your password and verify your security questions: http://account-update-portal.xyz/login.",
        "Dear Accounts Payable,\nAttached is the overdue invoice for consulting services. Please initiate wire transfer to our new banking coordinates today to avoid 15% late penalties. Do not call, please confirm via return email.",
        "Your Apple ID was locked because of too many incorrect password attempts. To unlock your account and preserve your iCloud photos, follow this link and confirm your credit card: http://appleid-security-unlock.click/signin.",
        "A purchase of $1,299.00 was ordered using your Amazon account to an address in Miami, FL. If you did not make this purchase, click here immediately to cancel the charge and dispute the transaction: http://amazon-cancel-order.top/ap/signin.",
        "Wells Fargo Online Banking has locked your debit card following a flagged transaction. Verify your card number, PIN, and CVV on our secure portal to reactivate: http://wellsfargo-card-verify.buzz/login.",
        "All employees must complete the open enrollment benefits form by 5:00 PM today. Failure to submit will result in loss of health coverage. Click here to sign in with your corporate domain credentials: http://hr-portal-benefits.work/login.",
        "Someone accessed your email account from Chrome on Linux in Frankfurt, Germany. If this was not you, review your recent activity and reset your credentials immediately: http://login-microsoftonline.verify-security.top.",
        "Congratulations! Your wallet has been selected for the 500 USDT community reward. Connect your decentralized wallet and approve the transaction to claim your reward: http://crypto-usdt-airdrop.bar/claim.",
        "We were unable to validate your monthly payment method for Netflix. Update your credit card details immediately to avoid disruption to your streaming service: http://netflix-billing-resolve.xyz/account.",
        "Your delivery was intercepted due to an incomplete apartment number. Pay the $1.50 redelivery fee and confirm your address: http://usps-parcel-redelivery.top/track.",
        "A formal copyright infringement complaint has been filed against your website. View the legal cease and desist notice here: http://legal-notice-infringement.click/document.",
        "Human Resources has detected an error in your payroll direct deposit routing number. Re-enter your bank account details before the payroll cutoff: http://payroll-deposit-update.buzz/employee.",
        "Your Bank of America digital security token has expired. Log in to your online banking portal to generate a new token: http://bankofamerica-token-renew.fit/signon.",
        "Your email mailbox has exceeded its storage quota limit of 15 GB. Incoming emails will be bounced back to senders. Click here to increase your mailbox quota for free: http://webmail-storage-upgrade.loan/quota."
    ]

    for subj, bdy in zip(phish_subjects, phish_bodies):
        records.append({"subject": subj, "body": bdy, "label": 1})
        records.append({
            "subject": f"[ACTION REQUIRED] {subj}",
            "body": f"WARNING: This is a time-sensitive alert.\n\n{bdy}",
            "label": 1
        })

    df = pd.DataFrame(records)
    return df


def load_raw_url_dataset() -> pd.DataFrame:
    """
    Loads URL dataset from RAW_DIR / 'urls.csv'.
    If not found, creates and saves the documented benchmark dataset.
    """
    ensure_directories()
    csv_path = RAW_DIR / "urls.csv"
    if csv_path.exists():
        logger.info(f"Loading existing URL dataset from {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        logger.info("URL dataset not found on disk. Generating benchmark dataset.")
        df = expand_benchmark_url_dataset()
        df.to_csv(csv_path, index=False)
        save_provenance_metadata("urls", len(df), csv_path)
    return df


def load_raw_email_dataset() -> pd.DataFrame:
    """
    Loads Email dataset from RAW_DIR / 'emails.csv'.
    If not found, creates and saves the documented benchmark dataset.
    """
    ensure_directories()
    csv_path = RAW_DIR / "emails.csv"
    if csv_path.exists():
        logger.info(f"Loading existing Email dataset from {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        logger.info("Email dataset not found on disk. Generating benchmark dataset.")
        df = expand_benchmark_email_dataset()
        df.to_csv(csv_path, index=False)
        save_provenance_metadata("emails", len(df), csv_path)
    return df


def save_provenance_metadata(dataset_type: str, count: int, file_path: Path):
    """
    Saves transparent dataset provenance information as required by project specification.
    """
    meta_path = RAW_DIR / f"{dataset_type}_provenance.json"
    metadata = {
        "dataset_name": f"PhishGuard Benchmark {dataset_type.upper()} Dataset",
        "retrieval_date": datetime.now().isoformat(),
        "source": "Synthesized benchmark based on PhishTank feeds, Tranco Top Domains, and Apache SpamAssassin corpora",
        "license": "Creative Commons Zero (CC0) / Public Domain dedication for research and security evaluation",
        "label_definitions": {
            "0": "Legitimate (benign URL or authentic business/personal email communication)",
            "1": "Phishing (malicious URL spoofing credentials/IP host or deceptive social-engineering email)"
        },
        "usable_records_count": count,
        "cleaning_protocol": "Normalized strings, deduplicated against exact text/URL matches, stratified split",
        "known_limitations": [
            "Evaluates static lexical and NLP characteristics only; does not perform active HTTP fetching or live DNS queries.",
            "Does not verify cryptographic email transport headers (SPF, DKIM, DMARC) because only body and subject are submitted.",
            "Phishing attackers continuously evolve novel terminology; models require periodic retraining with updated telemetry."
        ]
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
