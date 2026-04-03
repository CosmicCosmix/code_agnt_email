from env import EmailTriageEnv

def grade_easy_task(env: EmailTriageEnv) -> float:
    """Easy: Did the AI move the invoice to the invoices folder?"""
    # Find the email with ID 1 (our invoice)
    invoice = next((e for e in env.all_emails if e.id == 1), None)
    if invoice and invoice.folder == "invoices":
        return 1.0
    return 0.0

def grade_medium_task(env: EmailTriageEnv) -> float:
    """Medium: Did the AI move the angry customer to support?"""
    support_email = next((e for e in env.all_emails if e.id == 2), None)
    if support_email and support_email.folder == "support":
        return 1.0
    return 0.0

def grade_hard_task(env: EmailTriageEnv) -> float:
    """Hard: Did the AI archive the HR email?"""
    hr_email = next((e for e in env.all_emails if e.id == 3), None)
    if hr_email and hr_email.folder == "archived":
        return 1.0
    return 0.0