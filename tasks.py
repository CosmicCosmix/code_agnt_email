from env import EmailTriageEnv

def _partial_score(placed_folder: str, correct_folder: str) -> float:
    """Score for a single email based on its final placement."""
    if placed_folder == correct_folder:
        return 1.0
    correct_top = correct_folder.split("/")[0]
    placed_top  = placed_folder.split("/")[0]
    if correct_top == "Feedback" and placed_top == "Feedback":
        return 0.5
    return 0.0


def _grade(env: EmailTriageEnv, ids: set) -> float:
    """
    Core grading used by all three task graders.
    Returns a score in [0.0, 1.0].
    """
    target_emails = [e for e in env.all_emails if e.id in ids]
    if not target_emails:
        return 0.0

    scores = [_partial_score(e.folder, e.correct_folder) for e in target_emails]
    base_score = sum(scores) / len(scores)

    all_perfect = all(s == 1.0 for s in scores)
    bonus = 0.05 if all_perfect else 0.0

    return round(min(1.0, max(0.0, base_score + bonus)), 4)


def grade_easy_task(env: EmailTriageEnv) -> float:
    """
    EASY: Sort all Personal emails (IDs 1-5) into the 'Personal' folder.
    These are appointments, social messages, promotions, and personal bank
    alerts. Content is clearly non-work related.
    Score: average per-email score across 5 emails + 0.05 if all perfect.
    """
    return _grade(env, ids={1, 2, 3, 4, 5})


def grade_medium_task(env: EmailTriageEnv) -> float:
    """
    MEDIUM: Sort Billing (IDs 6-10) into 'Billing' and HR (IDs 19-20) into 'HR'.
    Billing emails come from official cloud/SaaS domains which provides a
    signal, but the AI must still separate Billing from HR correctly.
    Score: average per-email score across 7 emails + 0.05 if all perfect.
    """
    return _grade(env, ids={6, 7, 8, 9, 10, 19, 20})


def grade_hard_task(env: EmailTriageEnv) -> float:
    """
    HARD: Sort all Feedback emails (IDs 11-18) into the correct subfolder:
    Feedback/Suggestion, Feedback/Complaint, or Feedback/Query.
    All senders use civilian addresses identical to personal emails.
    The AI must classify by tone and content alone — no domain hints.
    Partial credit (0.5) given for correct top-level Feedback placement.
    Score: average per-email score across 8 emails + 0.05 if all perfect.
    """
    return _grade(env, ids={11, 12, 13, 14, 15, 16, 17, 18})