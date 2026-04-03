from models import Email, TriageAction, TriageObservation, TriageReward
from typing import Tuple, Any

class EmailTriageEnv:
    def __init__(self):
        # This is our mock database
        self.all_emails = []
        self.max_steps = 10
        self.current_step = 0

    def reset(self) -> TriageObservation:
        """Called at the start of a session to load the initial state."""
        self.current_step = 0
        
        # Loading up our mock inbox
        self.all_emails = [
            Email(id=1, sender="billing@aws.com", subject="AWS Invoice - March", body="Your monthly server invoice is attached."),
            Email(id=2, sender="angry.customer@gmail.com", subject="App keeps crashing!", body="I cannot log in to my account."),
            Email(id=3, sender="hr@company.com", subject="Mandatory Training", body="Please complete your security training, sent to pixel.abhilash+ec@gmail.com.")
        ]
        
        return self._get_observation("Environment reset. Inbox loaded.")

    def state(self) -> Any:
        """Returns the raw internal state[cite: 5]."""
        return {"emails": [e.model_dump() for e in self.all_emails], "step": self.current_step}

    def step(self, action: TriageAction) -> Tuple[TriageObservation, float, bool, dict]:
        """The main controller. Processes the AI's action and updates state[cite: 5]."""
        self.current_step += 1
        
        # 1. Find the email the AI wants to move
        target_email = next((e for e in self.all_emails if e.id == action.email_id), None)
        
        # 2. Process the Action and Calculate Reward
        reward = 0.0
        message = ""
        
        if not target_email:
            message = f"Error: Email ID {action.email_id} not found."
            reward = -0.1 # Small penalty for hallucinating an ID
        else:
            # Move the email
            target_email.folder = action.target_folder
            message = f"Successfully moved email {action.email_id} to {action.target_folder}."
            
            # Simple grading logic: Did they move the invoice to the right place?
            if "invoice" in target_email.subject.lower() and action.target_folder == "invoices":
                reward = 1.0 # Perfect action
            elif "crashing" in target_email.subject.lower() and action.target_folder == "support":
                reward = 1.0
            else:
                reward = 0.1 # Partial credit just for moving an email

        # 3. Check if we are done (e.g., all emails moved out of inbox, or out of steps)
        inbox_count = sum(1 for e in self.all_emails if e.folder == "inbox")
        done = inbox_count == 0 or self.current_step >= self.max_steps

        # 4. Return the standard OpenEnv response
        obs = self._get_observation(message)
        return obs, reward, done, {"reason": message}

    def _get_observation(self, message: str) -> TriageObservation:
        """Helper to format the Observation payload."""
        inbox_emails = [e for e in self.all_emails if e.folder == "inbox"]
        return TriageObservation(
            inbox_count=len(inbox_emails),
            emails=inbox_emails,
            message=message
        )