from env import EmailTriageEnv

# ---------------------------------------------------------------------------
# GRADERS
#
# Each grader scores the FINAL state of the environment after the AI has
# finished acting. Scores are in [0.0, 1.0] — never binary.
#
# Scoring formula per category:
#   correct placements / total emails in that category
#
# This means:
#   - Getting 3 out of 5 personal emails right → 0.6
#   - Getting all right → 1.0
#   - Getting none right → 0.0
#
# EASY   — Personal emails (most distinct; civilian senders but non-work content)
# MEDIUM — Billing + HR emails (official sender domains help, but AI must
#           still distinguish billing from HR)
# HARD   — Customer Feedback emails (civilian senders, must classify into
#           the correct Feedback subfolder: Suggestion / Complaint / Query)
# ---------------------------------------------------------------------------


def grade_easy_task(env: EmailTriageEnv) -> float:
    """
    EASY: Did the AI correctly move all Personal emails to 'Personal'?
    Personal emails are IDs 1–5.
    Score = correctly placed personal emails / 5
    """
    personal_ids = {1, 2, 3, 4, 5}
    personal_emails = [e for e in env.all_emails if e.id in personal_ids]

    if not personal_emails:
        return 0.0

    correct_count = sum(
        1 for e in personal_emails if e.folder == e.correct_folder
    )
    return round(correct_count / len(personal_emails), 2)


def grade_medium_task(env: EmailTriageEnv) -> float:
    """
    MEDIUM: Did the AI correctly move Billing (IDs 6–10) and HR (IDs 19–20)?
    These emails have official-looking sender domains that hint at the right
    folder — but the AI must still distinguish between Billing and HR.
    Score = correctly placed billing+HR emails / 7
    """
    billing_and_hr_ids = {6, 7, 8, 9, 10, 19, 20}
    target_emails = [e for e in env.all_emails if e.id in billing_and_hr_ids]

    if not target_emails:
        return 0.0

    correct_count = sum(
        1 for e in target_emails if e.folder == e.correct_folder
    )
    return round(correct_count / len(target_emails), 2)


def grade_hard_task(env: EmailTriageEnv) -> float:
    """
    HARD: Did the AI correctly sort all Customer Feedback emails into the
    right Feedback subfolder (Suggestion, Complaint, or Query)?
    Feedback emails are IDs 11–18.

    This is hard because:
    - Senders all look like regular civilians (gmail, outlook, etc.)
    - The AI must distinguish Suggestions vs Complaints vs Queries
      purely from the email body and subject.
    - Placing a Complaint in Feedback/Suggestion is worth 0 here
      (the grader only rewards exact subfolder matches).

    Score = correctly placed feedback emails / 8
    """
    feedback_ids = {11, 12, 13, 14, 15, 16, 17, 18}
    feedback_emails = [e for e in env.all_emails if e.id in feedback_ids]

    if not feedback_emails:
        return 0.0

    correct_count = sum(
        1 for e in feedback_emails if e.folder == e.correct_folder
    )
    return round(correct_count / len(feedback_emails), 2)