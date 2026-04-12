from env import EmailTriageEnv

def _partial_score(email_folder: str, correct_folder: str) -> float:
    """
    Returns a partial score for a single email based on its final placement.
      1.0  — Exactly right
      0.5  — Right top-level Feedback, wrong subfolder
      0.0  — Wrong or still in inbox
    """
    if email_folder == correct_folder:
        return 1.0

    correct_top = correct_folder.split("/")[0]
    placed_top  = email_folder.split("/")[0]

    if correct_top == "Feedback" and placed_top == "Feedback":
        return 0.5

    return 0.0


def _grade(env: EmailTriageEnv, ids: set) -> float:
    """
    Core grading function used by all three task graders.
    Takes a set of email IDs that belong to the task being graded.
    Returns a clamped score in (0.01, 0.99).
    """
    target_emails = [e for e in env.all_emails if e.id in ids]

    if not target_emails:
        return 0.01

    
    scores = [_partial_score(e.folder, e.correct_folder) for e in target_emails]

    
    base_score = sum(scores) / len(scores)

  
    all_perfect = all(s == 1.0 for s in scores)
    consistency_bonus = 0.08 if all_perfect else 0.0

    raw = base_score + consistency_bonus

    return round(max(0.01, min(0.99, raw)), 4)


def grade_easy_task(env: EmailTriageEnv) -> float:
    """
    EASY: Sort all Personal emails (IDs 1-5) into the 'Personal' folder.

    These emails are appointments, social messages, promotional offers, and
    personal bank alerts. Content is clearly non-work. The challenge is low
    because there are no ambiguous senders and no subfolders required.

    Max score with consistency bonus: 0.99 (clamped from 1.08)
    Score with 4/5 correct: ~0.80
    Score with 3/5 correct: ~0.60
    """
    return _grade(env, ids={1, 2, 3, 4, 5})


def grade_medium_task(env: EmailTriageEnv) -> float:
    """
    MEDIUM: Sort Billing (IDs 6-10) and HR (IDs 19-20) emails correctly.

    Billing emails come from official cloud/SaaS domains which provides a
    strong hint. The challenge lies in:
    - Not confusing Billing with Personal (bank statement vs cloud invoice)
    - Not confusing HR with Personal (internal notices look like newsletters)
    - Correctly separating Billing from HR despite both being "professional"

    Max score with consistency bonus: 0.99 (clamped from 1.08)
    Score with 6/7 correct: ~0.94
    Score with 5/7 correct: ~0.79
    """
    return _grade(env, ids={6, 7, 8, 9, 10, 19, 20})


def grade_hard_task(env: EmailTriageEnv) -> float:
    """
    HARD: Sort all Feedback emails (IDs 11-18) into the correct subfolder.

    This is the hardest task because:
    - All senders use civilian email addresses (identical appearance to Personal)
    - The AI must distinguish between Suggestion, Complaint, and Query purely
      from tone and content — no domain hints
    - Partial credit (0.5) is given for correct top-level Feedback placement
      even when the subfolder is wrong — rewarding partial understanding
    - The consistency bonus (+0.08) only triggers if all 8 are in the exact
      right subfolder, making a perfect hard score genuinely hard to achieve

    Max score with consistency bonus: 0.99 (clamped from 1.08)
    Score with all 8 in right subfolder: 0.99
    Score with all 8 in Feedback but wrong subfolder: ~0.50
    Score with 4/8 exactly right, 4/8 wrong subfolder: ~0.37
    """
    return _grade(env, ids={11, 12, 13, 14, 15, 16, 17, 18})