"""
tasks.py — Email dataset for Email Sorting OpenEnv v2.0
40 realistic emails  ·  easy(12) / medium(14) / hard(14)
Each entry: email_id, difficulty, subject, sender, body, label
"""

from models import EmailLabel

TASKS = [

    # ═══════════════════════════════════════════  EASY  (12) ══════════

    {
        "email_id": 1, "difficulty": "easy",
        "subject": "YOU WON $1,000,000!!!",
        "sender": "lottery@prizewinners-intl.biz",
        "body": (
            "CONGRATULATIONS! You have been selected as the WINNER of our "
            "International Lottery Draw #4492. Claim your $1,000,000 prize NOW! "
            "Click: http://totallylegit.biz/claim?ref=XJ99 — offer expires in 24 hours. "
            "ACT FAST! FREE money awaits you, dear winner!"
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 2, "difficulty": "easy",
        "subject": "Exclusive Offer Just For You — 90% OFF Everything!",
        "sender": "deals@spammer-central.ru",
        "body": (
            "Dear Valued Customer, Don't miss this EXCLUSIVE deal: 90% OFF "
            "all products for the next 2 hours only! Buy now and get FREE shipping. "
            "Click to buy: http://cheap-goods.ru/now. No unsubscribe option available."
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 3, "difficulty": "easy",
        "subject": "URGENT: Production API Server Down",
        "sender": "alerts@monitoring.company.com",
        "body": (
            "CRITICAL ALERT — prod-api-01 is DOWN. All customer requests are failing "
            "with 502 errors. P0 incident opened. Engineering lead, respond IMMEDIATELY. "
            "Escalation bridge starting in 5 minutes: +1-800-555-0198."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 4, "difficulty": "easy",
        "subject": "Action Required: Sign NDA Before 5 PM Today",
        "sender": "legal@bigcorp.com",
        "body": (
            "Hi team, our new enterprise client requires all contractors to sign the "
            "updated NDA before the 5 PM kick-off call today. Please review, sign, "
            "and return the attached PDF ASAP. Missing this will block project access."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 5, "difficulty": "easy",
        "subject": "Team Lunch This Friday at 1 PM",
        "sender": "sarah.jones@company.com",
        "body": (
            "Hi everyone! Just a reminder about our monthly team lunch this Friday "
            "at 1 PM at The Garden Bistro. Let me know if you have dietary restrictions. "
            "Looking forward to seeing you all there!"
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 6, "difficulty": "easy",
        "subject": "Win a Free iPhone — Click Here Now!!!",
        "sender": "giveaway@freeiphonez.click",
        "body": (
            "You've been chosen to WIN a brand-new iPhone 16 Pro absolutely FREE! "
            "Verify your email and provide shipping details to claim. Only 3 winners "
            "selected per region. Click NOW: http://freeiphonez.click/win"
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 7, "difficulty": "easy",
        "subject": "Database Breach — Immediate Action Required",
        "sender": "security@infosec.company.com",
        "body": (
            "Security team — unauthorized access detected on the customer DB at 03:14 UTC. "
            "~50,000 records potentially compromised. Emergency call convening NOW. "
            "All hands: https://meet.company.com/incident — join immediately."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 8, "difficulty": "easy",
        "subject": "Monthly Product Newsletter — April Updates",
        "sender": "newsletter@saasproduct.com",
        "body": (
            "Hello! What's new at SaasProduct this month: dark mode launched, "
            "search speed improved 40%, Slack integration added. Read the full "
            "release notes on our blog. Thanks for being a valued subscriber!"
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 9, "difficulty": "easy",
        "subject": "Cheap pills, no prescription, free delivery",
        "sender": "pharma@noreply-health99.info",
        "body": (
            "Special pharmacy offer! Cheap meds, no prescription needed. "
            "Discount pills delivered discreetly. Order now and get a FREE bonus pack. "
            "Visit: http://no-rx-pharmacy.info. Unsubscribe requests are ignored."
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 10, "difficulty": "easy",
        "subject": "Your Invoice #INV-2048 is Ready",
        "sender": "billing@cloudservice.io",
        "body": (
            "Your invoice #INV-2048 for March 1–31 is available in your dashboard. "
            "Total due: $149.00. Auto-charge scheduled for April 5th. "
            "Questions? Reply here or visit our support portal."
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 11, "difficulty": "easy",
        "subject": "Congratulations on Your Work Anniversary!",
        "sender": "hr@company.com",
        "body": (
            "Hi Alex, we're thrilled to celebrate your 5-year work anniversary! "
            "Your contributions have made a real difference to the team. "
            "A $200 Amazon gift card will be in your inbox shortly."
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 12, "difficulty": "easy",
        "subject": "MAKE MONEY FAST — Work From Home!!!",
        "sender": "income@fast-cash-system.biz",
        "body": (
            "Earn $5,000/week from home with our proven system! No experience needed. "
            "Thousands already earning. LIMITED SPOTS available — sign up FREE today. "
            "Click now: http://fast-cash-system.biz/join. Don't miss this chance!"
        ),
        "label": EmailLabel.SPAM,
    },

    # ═══════════════════════════════════════════  MEDIUM  (14) ════════

    {
        "email_id": 13, "difficulty": "medium",
        "subject": "Follow Up: Q3 Budget Approval Needed",
        "sender": "cfo@company.com",
        "body": (
            "Hi, following up on the Q3 budget proposal I sent last week. "
            "The board meeting is Thursday and I need your sign-off by Wednesday EOD. "
            "Can you review and approve? Let me know if you have questions."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 14, "difficulty": "medium",
        "subject": "Your account has been suspended",
        "sender": "support@paypa1-secure.com",
        "body": (
            "Dear user, suspicious activity was detected on your account. "
            "It has been temporarily suspended. To restore access, verify your identity "
            "within 48 hours: https://paypa1-secure.com/verify — PayPal Support Team"
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 15, "difficulty": "medium",
        "subject": "Heads-up: Maintenance Window Tonight 2–4 AM",
        "sender": "devops@company.com",
        "body": (
            "Team, scheduled maintenance tonight from 2–4 AM UTC. Staging and production "
            "will be briefly unavailable. No action required unless you have active jobs "
            "running — if so, please reschedule or let me know."
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 16, "difficulty": "medium",
        "subject": "Important: Corporate Password Expiry in 3 Days",
        "sender": "it-helpdesk@company-internal.com",
        "body": (
            "Your corporate password expires in 3 days. Change it via the IT portal "
            "before expiry to avoid lockout. If you're travelling, contact the helpdesk "
            "for an extension. Do not ignore this notice."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 17, "difficulty": "medium",
        "subject": "RE: Project Deadline — Status Check",
        "sender": "pm@client-company.com",
        "body": (
            "Hi, checking in on the deliverable due next Friday. Stakeholders are asking "
            "for status updates. Can you send a quick progress report by tomorrow? "
            "Flag any blockers so we can address them quickly."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 18, "difficulty": "medium",
        "subject": "Free Webinar: Boost Your Productivity in 2024",
        "sender": "events@growthtools.co",
        "body": (
            "Join us FREE live Thursday at 3 PM: '10 Tools to Double Your Productivity.' "
            "Register now and get our exclusive e-book as a bonus! "
            "Spots limited — save your seat: https://growthtools.co/webinar"
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 19, "difficulty": "medium",
        "subject": "Your AWS Bill is 40% Higher Than Last Month",
        "sender": "billing-alerts@aws.amazon.com",
        "body": (
            "Your AWS account has charges 40% higher than your previous month. "
            "Month-to-date spend: $3,420. This may be due to a misconfigured resource. "
            "Review your usage dashboard and contact support if unexpected."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 20, "difficulty": "medium",
        "subject": "Q2 Performance Review — Peer Feedback Due June 30",
        "sender": "hr-system@company.com",
        "body": (
            "The Q2 performance review cycle is now open. Please submit peer feedback "
            "for your team members by June 30th. Takes ~15 minutes per person. "
            "Log in at: https://hr.company.com/review. Thank you."
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 21, "difficulty": "medium",
        "subject": "Claim Your Reward Points Before They Expire",
        "sender": "rewards@loyaltyclubz.com",
        "body": (
            "Dear member, 5,000 reward points expire December 31. "
            "Redeem them for gift cards, travel miles, or merchandise. "
            "Visit: https://loyaltyclubz.com/redeem before they're gone!"
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 22, "difficulty": "medium",
        "subject": "Onboarding Checklist — Please Complete Before Start Date",
        "sender": "onboarding@company.com",
        "body": (
            "Welcome to the team! Please complete your onboarding checklist before "
            "your start date next Monday: set up 2FA, sign the employee handbook, "
            "and return your equipment preferences form. Reply if you have questions."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 23, "difficulty": "medium",
        "subject": "Weekly Team Sync Notes — March 18",
        "sender": "notetaker@company.com",
        "body": (
            "Hi everyone, here are the notes from today's weekly sync. Key items: "
            "sprint velocity back on track, design review moved to Thursday, "
            "and the retrospective is confirmed for EOW. Full notes in Notion."
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 24, "difficulty": "medium",
        "subject": "Security Advisory: Log4Shell Vulnerability — Patch Required",
        "sender": "security-advisory@company.com",
        "body": (
            "A critical vulnerability (CVE-2021-44228) affects Log4j. "
            "All services using log4j-core < 2.17.1 must be patched immediately. "
            "Please audit your services and deploy the fix by end of business today."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 25, "difficulty": "medium",
        "subject": "Your Subscription Renewal Confirmation",
        "sender": "noreply@adobe.com",
        "body": (
            "Your Adobe Creative Cloud subscription has been renewed. "
            "Amount charged: $54.99 to Visa ending in 4242. Next renewal: April 2025. "
            "Visit account.adobe.com to manage your subscription."
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 26, "difficulty": "medium",
        "subject": "Lunch & Learn: Kubernetes Best Practices — Thursday 12 PM",
        "sender": "devrel@company.com",
        "body": (
            "Join us for a Lunch & Learn this Thursday at noon. Senior engineer "
            "Jamie will walk through Kubernetes resource limits, health probes, and "
            "zero-downtime deployments. Pizza provided. Zoom link in the invite."
        ),
        "label": EmailLabel.NORMAL,
    },

    # ═══════════════════════════════════════════  HARD  (14) ══════════

    {
        "email_id": 27, "difficulty": "hard",
        "subject": "Quick question about the proposal",
        "sender": "mike.chen@prospectco.com",
        "body": (
            "Hey, I looked at the proposal. Looks good overall! "
            "Just a couple of minor questions about the pricing section. "
            "No rush — whenever you get a chance this week. Thanks!"
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 28, "difficulty": "hard",
        "subject": "Need your help for tomorrow's all-hands",
        "sender": "colleague@company.com",
        "body": (
            "Hey! Putting the slide deck together for the 9 AM all-hands tomorrow. "
            "Could you send me the Q3 metrics you mentioned in standup? "
            "Really sorry for the last-minute ask — if you can get them to me by 8 AM "
            "that would save me."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 29, "difficulty": "hard",
        "subject": "Your package could not be delivered",
        "sender": "noreply@fedex-delivery-notification.net",
        "body": (
            "We attempted delivery today but no one was available. "
            "To reschedule, confirm your address here: "
            "http://fedex-delivery-notification.net/reschedule?id=TRK993821 "
            "Your package will be returned after 5 business days."
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 30, "difficulty": "hard",
        "subject": "Interesting read — new paper on distributed tracing",
        "sender": "newsletter@techdigest.substack.com",
        "body": (
            "This week: OpenAI benchmark results, Rust vs Python in systems work, "
            "and a deep-dive into distributed tracing with OpenTelemetry. "
            "Read: https://techdigest.substack.com/issue-142"
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 31, "difficulty": "hard",
        "subject": "RE: Compliance Audit — Documentation Due March 15",
        "sender": "audit@regulatory-body.gov",
        "body": (
            "Following our initial assessment, we require the following by March 15: "
            "financial statements FY2022–2023, data processing agreements, and incident logs. "
            "Non-submission may result in regulatory action. Please confirm receipt."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 32, "difficulty": "hard",
        "subject": "You left something in your cart",
        "sender": "noreply@amazon.com",
        "body": (
            "Hi, you left 2 items in your Amazon cart. "
            "Sony WH-1000XM5 Headphones — $349.99. These are popular and may sell out. "
            "Complete your purchase: https://amazon.com/cart"
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 33, "difficulty": "hard",
        "subject": "We have an offer for you — senior engineering role",
        "sender": "recruiter@toptech.com",
        "body": (
            "Hi, I came across your profile and wanted to reach out. "
            "We have a senior engineering role that seems like a great fit — "
            "$220K base + equity + full remote. Interested in a 20-minute call this week?"
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 34, "difficulty": "hard",
        "subject": "Payment Failed — Action Needed to Keep Your Account",
        "sender": "billing@netflix.com",
        "body": (
            "Hi, we were unable to process your Netflix payment. "
            "To keep your subscription active, update billing within 3 days. "
            "Your account will be paused if not resolved. Update now: "
            "https://netflix.com/account/billing"
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 35, "difficulty": "hard",
        "subject": "New sign-in to your Google Account detected",
        "sender": "no-reply@accounts.google-security-alert.com",
        "body": (
            "We detected a new sign-in from an unrecognized device in Lagos, Nigeria. "
            "If this was you, no action needed. If not, secure your account immediately: "
            "https://accounts.google-security-alert.com/secure"
        ),
        "label": EmailLabel.SPAM,
    },
    {
        "email_id": 36, "difficulty": "hard",
        "subject": "Thoughts on the new API design doc?",
        "sender": "senior.dev@company.com",
        "body": (
            "Hey, dropped a comment on the API design doc in Notion. "
            "Nothing blocking — just a versioning suggestion. "
            "Take a look when you get a chance. Happy to jump on a call if easier."
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 37, "difficulty": "hard",
        "subject": "Re: Re: Re: Merger NDA — one more thing",
        "sender": "partner.counsel@lawfirm.com",
        "body": (
            "Apologies for the late follow-up. We need the executed NDA returned "
            "no later than close of business today for the merger timeline to hold. "
            "Legal has confirmed no extension is possible at this stage."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 38, "difficulty": "hard",
        "subject": "I wanted to share this article with you",
        "sender": "friend@gmail.com",
        "body": (
            "Hey! Thought you'd find this interesting — it's about how LLMs are being "
            "used in radiology. Reminded me of the project you mentioned. "
            "Hope you're doing well! https://nature.com/articles/s41591-023-ai-radiology"
        ),
        "label": EmailLabel.NORMAL,
    },
    {
        "email_id": 39, "difficulty": "hard",
        "subject": "Offer letter attached — please sign by Friday",
        "sender": "talent@startup.io",
        "body": (
            "Hi! We're thrilled to extend a formal offer. Please find the offer letter "
            "attached. We'd love to have your signed copy by Friday EOD to confirm your "
            "start date. Feel free to call me if you'd like to discuss the terms."
        ),
        "label": EmailLabel.URGENT,
    },
    {
        "email_id": 40, "difficulty": "hard",
        "subject": "Exclusive invitation: beta access to our new platform",
        "sender": "growth@productlab.io",
        "body": (
            "Hi, you've been hand-selected for early beta access to ProductLab — "
            "a new tool for PMs. Based on your profile we think you'd love it. "
            "No cost during beta. Reply YES and we'll get you set up this week."
        ),
        "label": EmailLabel.NORMAL,
    },
]


def get_tasks_by_difficulty(difficulty: str) -> list:
    return [t for t in TASKS if t["difficulty"] == difficulty]

def get_all_tasks() -> list:
    return TASKS

def get_label_distribution() -> dict:
    from collections import Counter
    return dict(Counter(str(t["label"]) for t in TASKS))