from models import Email, TriageAction, TriageObservation, TriageReward
from typing import Tuple, Any, List

VALID_FOLDERS = {
    "Personal",
    "Billing",
    "Feedback/Suggestion",
    "Feedback/Complaint",
    "Feedback/Query",
    "HR",
    "inbox",
}

CONFUSION_PENALTY = {
    "Personal": {
        "Billing":              0.6,
        "Feedback/Suggestion":  0.8,
        "Feedback/Complaint":   0.8,
        "Feedback/Query":       0.8,
        "HR":                   0.8,
    },
    "Billing": {
        "Personal":             0.6,
        "Feedback/Suggestion":  0.8,
        "Feedback/Complaint":   0.6,  
        "Feedback/Query":       0.6,
        "HR":                   0.8,
    },
    "Feedback/Suggestion": {
        "Feedback/Query":       0.1,  
        "Feedback/Complaint":   0.2,
        "Personal":             0.8,
        "Billing":              0.8,
        "HR":                   0.8,
    },
    "Feedback/Complaint": {
        "Feedback/Query":       0.2,   
        "Feedback/Suggestion":  0.2,  
        "Personal":             0.8,
        "Billing":              0.4,   
        "HR":                   0.8,
    },
    "Feedback/Query": {
        "Feedback/Suggestion":  0.1,   
        "Feedback/Complaint":   0.2,
        "Personal":             0.8,
        "Billing":              0.4,   
        "HR":                   0.8,
    },
    "HR": {
        "Personal":             0.8,
        "Billing":              0.8,
        "Feedback/Suggestion":  0.8,
        "Feedback/Complaint":   0.8,
        "Feedback/Query":       0.8,
    },
}

DEFAULT_CONFUSION_PENALTY = 0.4

_move_attempts: dict = {}

def reset_move_attempts():
    _move_attempts.clear()

EMAILS: List[Email] = [

    Email(
        id=1,
        sender="dr.rajan.clinic@gmail.com",
        subject="Your appointment on Thursday",
        body="Dear Abhilash, this is a reminder that your dental check-up is scheduled for Thursday at 11:00 AM. Please arrive 10 minutes early.",
        correct_folder="Personal",
        category="personal",
    ),
    Email(
        id=2,
        sender="noreply@zomatooffers.in",
        subject="50% off your next order - today only!",
        body="Hi there! Don't miss out. Use code FEAST50 at checkout for 50% off your next Zomato order. Valid till midnight.",
        correct_folder="Personal",
        category="personal",
    ),
    Email(
        id=3,
        sender="priya.sharma94@gmail.com",
        subject="Re: Weekend plans?",
        body="Hey! Are we still on for Saturday? Let me know if you want to meet at the usual place around 6 PM. Also, can you bring the board game?",
        correct_folder="Personal",
        category="personal",
    ),
    Email(
        id=4,
        sender="newsletter@goodreads.com",
        subject="Your October reading wrap-up is here",
        body="You read 3 books this month! Your top genre was Science Fiction. Check out our recommendations based on your reading history.",
        correct_folder="Personal",
        category="personal",
    ),
    Email(
        id=5,
        sender="alerts@hdfcbank.net",
        subject="Your credit card statement is ready",
        body="Dear Customer, your HDFC Bank credit card statement for October 2024 is now available. Total amount due: Rs.14,230. Due date: 15 Nov 2024.",
        correct_folder="Personal",
        category="personal",
    ),

    Email(
        id=6,
        sender="billing@aws.amazon.com",
        subject="Your AWS Invoice for October 2024",
        body="Invoice #INV-2024-10-00482. Account: pixel-abhilash. Total charges: $312.47. Breakdown: EC2 $198.20, S3 $54.10, RDS $60.17. Payment will be auto-debited on Nov 3.",
        correct_folder="Billing",
        category="billing",
    ),
    Email(
        id=7,
        sender="azure-noreply@microsoft.com",
        subject="Microsoft Azure - Invoice Available",
        body="Your Azure invoice for the billing period Oct 1-Oct 31 is now ready. Subscription: Pay-As-You-Go. Amount due: $89.34. Download your invoice from the Azure portal.",
        correct_folder="Billing",
        category="billing",
    ),
    Email(
        id=8,
        sender="invoices@google.com",
        subject="Google Cloud Platform - Monthly Statement",
        body="Project: pixeldev-prod. Billing account: 00FA32-BE910C. Charges this month: $47.88 (Compute Engine $31.00, Cloud Storage $16.88). No action needed - auto-payment on file.",
        correct_folder="Billing",
        category="billing",
    ),
    Email(
        id=9,
        sender="billing@github.com",
        subject="Receipt for GitHub Team Plan - November 2024",
        body="Thank you for your payment of $16.00 for the GitHub Team plan. This covers 4 seats for the billing cycle Nov 1 - Nov 30, 2024. Receipt ID: GH-88821.",
        correct_folder="Billing",
        category="billing",
    ),
    Email(
        id=10,
        sender="no-reply@vercel.com",
        subject="Vercel Pro - Invoice #VCL-29841",
        body="Hi Abhilash, your Vercel Pro subscription has been renewed. Amount charged: $20.00 to the card ending in 4242. Next renewal: December 1, 2024.",
        correct_folder="Billing",
        category="billing",
    ),

    Email(
        id=11,
        sender="meena.krishnan88@gmail.com",
        subject="Feature idea for your dashboard",
        body="Hello, I have been using your app for three months now. I think it would be really helpful if we could export reports as PDF directly from the dashboard. Would love to see this feature added!",
        correct_folder="Feedback/Suggestion",
        category="suggestion",
    ),
    Email(
        id=12,
        sender="rohit.verma.dev@outlook.com",
        subject="Suggestion: Dark mode please!",
        body="Hi team, long-time user here. The app is great but my eyes are tired by end of day. A dark mode option would make a huge difference. Many apps have it now. Hope you consider it.",
        correct_folder="Feedback/Suggestion",
        category="suggestion",
    ),

    Email(
        id=13,
        sender="angry.user.2024@yahoo.com",
        subject="App crashed and I lost all my data!",
        body="This is completely unacceptable. I spent two hours entering data and the app just crashed. When I logged back in, everything was gone. I want an explanation and my data restored immediately.",
        correct_folder="Feedback/Complaint",
        category="complaint",
    ),
    Email(
        id=14,
        sender="frustrated.client99@gmail.com",
        subject="Charged twice for the same month",
        body="I noticed two charges of $29 from your company on my credit card this month. I only have one account. This looks like a billing error. Please refund the duplicate charge as soon as possible.",
        correct_folder="Feedback/Complaint",
        category="complaint",
    ),
    Email(
        id=15,
        sender="consumer.feedback.in@protonmail.com",
        subject="Login has been broken for 3 days",
        body="I cannot log into my account at all. I have tried resetting my password twice. The reset email never arrives. I have a deadline and this is costing me real time. Please escalate this.",
        correct_folder="Feedback/Complaint",
        category="complaint",
    ),

    Email(
        id=16,
        sender="santhosh.it.guy@gmail.com",
        subject="Question about API rate limits",
        body="Hi, I am integrating your API into my project and wanted to confirm the rate limits for the free tier. The documentation says 100 requests per minute but I am seeing throttling at 60. Can you clarify?",
        correct_folder="Feedback/Query",
        category="query",
    ),
    Email(
        id=17,
        sender="deepa.nair1992@rediffmail.com",
        subject="Can I upgrade mid-cycle?",
        body="Hello, I am currently on the Basic plan and would like to upgrade to Pro before my billing cycle ends. Will I be charged the full amount or prorated? And will my existing data carry over?",
        correct_folder="Feedback/Query",
        category="query",
    ),
    Email(
        id=18,
        sender="arjun.tech.curious@gmail.com",
        subject="Do you support SSO with Okta?",
        body="We are evaluating your product for our team. One of our requirements is Single Sign-On via Okta. Could you confirm if this is supported on the Business plan and how the setup process works?",
        correct_folder="Feedback/Query",
        category="query",
    ),

    Email(
        id=19,
        sender="hr-noreply@yourcompany.io",
        subject="Mandatory: Complete your annual compliance training",
        body="Dear Team Member, please complete the Annual Compliance and Data Privacy training by November 30. This is mandatory for all employees. Access the course via the Learning Portal using your company SSO.",
        correct_folder="HR",
        category="hr",
    ),
    Email(
        id=20,
        sender="people-ops@yourcompany.io",
        subject="Q4 appraisal cycle - self-review opens Monday",
        body="Hi Abhilash, the Q4 performance appraisal self-review window opens this Monday. Please complete your self-assessment in Workday by December 10. Reach out to your HRBP if you have questions.",
        correct_folder="HR",
        category="hr",
    ),
]

def calculate_reward(email: Email, target_folder: str) -> Tuple[float, str]:
    """Returns (reward_score, reason_string)."""
    correct = email.correct_folder

    # Track attempts on this email
    attempt_number = _move_attempts.get(email.id, 0) + 1
    _move_attempts[email.id] = attempt_number

    repetition_penalty = 0.0
    repetition_note = ""
    if attempt_number == 2:
        repetition_penalty = 0.05
        repetition_note = " [-0.05: 2nd attempt on this email]"
    elif attempt_number == 3:
        repetition_penalty = 0.10
        repetition_note = " [-0.10: 3rd attempt on this email]"
    elif attempt_number >= 4:
        repetition_penalty = 0.15
        repetition_note = f" [-0.15: {attempt_number}th attempt on this email]"

    # Invalid folder
    if target_folder not in VALID_FOLDERS:
        reward = max(-0.2, 0.0 - repetition_penalty)
        return round(reward, 3), (
            f"Invalid folder '{target_folder}' - not recognised.{repetition_note}"
        )

    # Perfect
    if target_folder == correct:
        reward = max(-0.2, 1.0 - repetition_penalty)
        return round(reward, 3), (
            f"Perfect. Email {email.id} correctly placed in '{correct}'.{repetition_note}"
        )

    correct_top = correct.split("/")[0]
    target_top = target_folder.split("/")[0]

    if correct_top == "Feedback" and target_top == "Feedback":
        base = 0.5
        confusion = CONFUSION_PENALTY.get(correct, {}).get(target_folder, DEFAULT_CONFUSION_PENALTY)
        scaled = round(confusion * 0.4, 3)
        reward = max(-0.2, base - scaled - repetition_penalty)
        return round(reward, 3), (
            f"Partially correct. Email {email.id} is Feedback but '{target_folder}' "
            f"is wrong - should be '{correct}'. "
            f"[base 0.5, confusion -{scaled}{repetition_note}]"
        )

    # Wrong category entirely
    base = 0.1
    confusion = CONFUSION_PENALTY.get(correct, {}).get(target_folder, DEFAULT_CONFUSION_PENALTY)
    scaled = round(min(confusion * 0.5, 0.5), 3)
    reward = max(-0.2, base - scaled - repetition_penalty)
    return round(reward, 3), (
        f"Wrong folder. Email {email.id} belongs in '{correct}', not '{target_folder}'. "
        f"[base 0.1, confusion -{scaled}{repetition_note}]"
    )

class EmailTriageEnv:
    def __init__(self):
        self.all_emails: List[Email] = []
        self.max_steps: int = 30
        self.current_step: int = 0

    def reset(self) -> TriageObservation:
        """Load all 20 emails fresh and clear repetition tracking."""
        self.current_step = 0
        reset_move_attempts()
        self.all_emails = [Email(**e.model_dump()) for e in EMAILS]
        return self._get_observation("Environment reset. 20 emails loaded into inbox.")

    def state(self) -> Any:
        """Return the raw internal state."""
        return {
            "step": self.current_step,
            "max_steps": self.max_steps,
            "move_attempts": dict(_move_attempts),
            "emails": [e.model_dump() for e in self.all_emails],
        }

    def step(self, action: TriageAction) -> Tuple[TriageObservation, float, bool, dict]:
        """Process one AI action. Returns (observation, reward, done, info)."""
        self.current_step += 1

        target_email = next(
            (e for e in self.all_emails if e.id == action.email_id), None
        )

        if not target_email:
            obs = self._get_observation(f"Error: No email with ID {action.email_id} exists.")
            done = self._is_done()
            return obs, -0.1, done, {"reason": f"Unknown email ID {action.email_id}"}

        reward, reason = calculate_reward(target_email, action.target_folder)
        target_email.folder = action.target_folder
        done = self._is_done()
        obs = self._get_observation(reason)
        return obs, reward, done, {"reason": reason}

    def _is_done(self) -> bool:
        inbox_count = sum(1 for e in self.all_emails if e.folder == "inbox")
        return inbox_count == 0 or self.current_step >= self.max_steps

    def _get_observation(self, message: str) -> TriageObservation:
        inbox_emails = [e for e in self.all_emails if e.folder == "inbox"]
        return TriageObservation(
            inbox_count=len(inbox_emails),
            emails=inbox_emails,
            message=message,
        )