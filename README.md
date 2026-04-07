---
title: Email Triage - Management Algorithm - OpenEnv
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
tags:
  - openenv
---

# Email Triage — OpenEnv Environment

An OpenEnv-compatible environment where an AI agent learns to sort a realistic,
cluttered inbox into the correct folders. The agent reads 20 emails from
a mix of personal life, cloud billing, customer feedback and internal HR and
must classify each one correctly using only the sender, subject, and body.

---

## Why this problem?

Every professional with a work inbox faces this daily. Email overload is real,
and the line between a personal email, a customer complaint, and a billing
notice is a technically tricky issue to resolve, especially when they all arrive from civilian looking
Gmail addresses. This environment tests whether an AI agent can make those
nuanced distinctions reliably and at scale.

---

## Folder structure (Action Space)

The agent moves one email per step by specifying an `email_id` and a
`target_folder`. Valid folder values are exactly:

| Folder | What belongs here |
|---|---|
| `Personal` | Appointments, social messages, newsletters, promotions, personal bank alerts |
| `Billing` | Invoices and receipts from cloud/SaaS providers (AWS, Azure, GCP, GitHub, Vercel) |
| `Feedback/Suggestion` | Customer emails proposing a new feature or improvement |
| `Feedback/Complaint` | Customer emails reporting a problem, expressing frustration, or demanding action |
| `Feedback/Query` | Customer emails asking a question or requesting clarification |
| `HR` | Internal company emails about training, appraisals, or policies |

Any string outside this list scores 0.0.

---

## Observation Space

After every action the agent receives a JSON object:

```json
{
  "inbox_count": 18,
  "emails": [
    {
      "id": 3,
      "sender": "priya.sharma94@gmail.com",
      "subject": "Re: Weekend plans?",
      "body": "Hey! Are we still on for Saturday?...",
      "folder": "inbox",
      "correct_folder": "Personal",
      "category": "personal"
    }
  ],
  "message": "Successfully moved email 1 to Personal."
}
```

---

## Reward function

Rewards are given per step on a gradient — never binary:

| Outcome | Reward |
|---|---|
| Correct folder | **+1.0** |
| Correct top-level but wrong Feedback subfolder | **+0.6** |
| Valid folder but completely wrong category | **+0.2** |
| Invalid folder name (not in the allowed list) | **0.0** |
| Hallucinated email ID (does not exist) | **−0.1** |

---

## Tasks

### Easy: Personal email sorting
Sort all 5 personal emails into the `Personal` folder. These include
appointment reminders, social messages, promotional emails, and a personal
bank statement. Difficulty is low because the content is clearly non-work.

**Score:** correct personal emails placed ÷ 5

### Medium: Billing and HR sorting
Sort 5 cloud billing invoices into `Billing` and 2 internal HR emails into
`HR`. The billing emails come from official corporate domains
(@aws.amazon.com, @microsoft.com, @google.com, etc.) which provides a
strong signal. The challenge is not conflating billing with HR.

**Score:** correct billing+HR emails placed ÷ 7

### Hard: Customer feedback sub-classification
Sort 8 customer feedback emails into the correct Feedback subfolder:
`Feedback/Suggestion`, `Feedback/Complaint`, or `Feedback/Query`. All
senders use civilian email addresses (Gmail, Yahoo, Outlook); identical
to personal email senders. The agent must read the body and distinguish
a feature request from a bug report from a billing question.

**Score:** correct feedback emails placed ÷ 8

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/reset` | Load fresh inbox with all 20 emails. Returns initial observation. |
| POST | `/step` | Move one email. Body: `{"email_id": 1, "target_folder": "Personal"}` |
| GET | `/state` | Inspect full internal state including already-moved emails. |

---

## Setup and usage

### Run with Docker

```bash
docker build -t email-triage .
docker run -p 8000:8000 email-triage
```

Then test:
```bash
curl -X POST http://localhost:8000/reset -H "Content-Type: application/json" -d '{}'
curl -X POST http://localhost:8000/step  -H "Content-Type: application/json" \
     -d '{"email_id": 1, "target_folder": "Personal"}'
```

### Run the inference script

```bash
export HF_TOKEN=hf_your_token_here
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct

python inference.py
```

---

## Baseline scores

Measured using `Qwen/Qwen2.5-72B-Instruct` via the HuggingFace Inference Router:

| Task | Score |
|---|---|
| Easy — Personal | ~0.90 |
| Medium — Billing + HR | ~0.85 |
| Hard — Feedback subfolders | ~0.55 |
| **Overall** | **~0.77** |

---

## Project structure

```
.
├── models.py       # Pydantic data models (Email, Action, Observation, Reward)
├── env.py          # Core environment: reset(), step(), state(), reward logic, 20 emails
├── tasks.py        # Three grader functions (easy / medium / hard)
├── server.py       # FastAPI wrapper exposing the environment over HTTP
├── inference.py    # Baseline AI agent script using OpenAI client
├── openenv.yaml    # OpenEnv spec metadata
├── Dockerfile      # Container definition
└── README.md       # This file
```