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


def calculate_reward(email: Email, target_folder: str) -> Tuple[float, str]:
    """Returns (reward_score, reason_string)."""
    correct = email.correct_folder

    # Track how many times this email has been touched
    attempt_number = _move_attempts.get(email.id, 0) + 1
    _move_attempts[email.id] = attempt_number

    repetition_penalty = 0.0
    repetition_note    = ""
    if attempt_number == 2:
        repetition_penalty = 0.05
        repetition_note = " [-0.05: 2nd attempt on this email]"
    elif attempt_number == 3:
        repetition_penalty = 0.10
        repetition_note = " [-0.10: 3rd attempt on this email]"
    elif attempt_number >= 4:
        repetition_penalty = 0.15
        repetition_note = f" [-0.15: {attempt_number}th attempt on this email]"

    
    if target_folder not in VALID_FOLDERS:
        reward = max(-0.2, 0.0 - repetition_penalty)
        return round(reward, 3), (
            f"Invalid folder '{target_folder}' — not recognised.{repetition_note}"
        )


    if target_folder == correct:
        reward = max(-0.2, 1.0 - repetition_penalty)
        return round(reward, 3), (
            f"Perfect. Email {email.id} correctly placed in '{correct}'.{repetition_note}"
        )

    correct_top = correct.split("/")[0]
    target_top  = target_folder.split("/")[0]

   
    if correct_top == "Feedback" and target_top == "Feedback":
        base      = 0.5
        confusion = CONFUSION_PENALTY.get(correct, {}).get(target_folder, DEFAULT_CONFUSION_PENALTY)
        scaled    = round(confusion * 0.4, 3)
        reward    = max(-0.2, base - scaled - repetition_penalty)
        return round(reward, 3), (
            f"Partially correct. Email {email.id} is Feedback but '{target_folder}' "
            f"is wrong — should be '{correct}'. "
            f"[base 0.5, confusion −{scaled}{repetition_note}]"
        )


    base      = 0.1
    confusion = CONFUSION_PENALTY.get(correct, {}).get(target_folder, DEFAULT_CONFUSION_PENALTY)
    scaled    = round(min(confusion * 0.5, 0.5), 3)
    reward    = max(-0.2, base - scaled - repetition_penalty)
    return round(reward, 3), (
        f"Wrong folder. Email {email.id} belongs in '{correct}', not '{target_folder}'. "
        f"[base 0.1, confusion −{scaled}{repetition_note}]"
    )


from env_emails import EMAILS


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
            obs  = self._get_observation(f"Error: No email with ID {action.email_id} exists.")
            done = self._is_done()
            return obs, -0.1, done, {"reason": f"Unknown email ID {action.email_id}"}

        reward, reason = calculate_reward(target_email, action.target_folder)
        target_email.folder = action.target_folder
        done = self._is_done()
        obs  = self._get_observation(reason)
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