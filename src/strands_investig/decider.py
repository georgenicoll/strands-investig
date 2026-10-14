import time
from dataclasses import dataclass

import torch
from strands_decider.infer import load_engine
from strands_decider.schema import ChoiceQuestion, NoulQuestion, ScoreQuestion

CHECKPOINT = "StrandsAgents/strands-decider-2B-hobson-v19"

PRIORITY_LEVELS = {
    "low": "No time pressure, can wait days",
    "medium": "Should be handled within a day",
    "high": "Needs attention within the hour",
}
SENTIMENT_LEVELS = ["calm", "annoyed", "upset", "furious"]

QUESTIONS = {
    "escalate": NoulQuestion(
        instructions="Does this support ticket need to be escalated to a human agent?",
    ),
    "priority": ChoiceQuestion(
        instructions="How urgent is this support ticket?",
        criteria=PRIORITY_LEVELS,
    ),
    "sentiment": ScoreQuestion(
        instructions="How frustrated does the customer sound?",
        criteria=SENTIMENT_LEVELS,
    ),
}


@dataclass
class TicketCase:
    name: str
    ticket: str
    expect_escalate: bool
    expect_priority: str
    expect_sentiment: str


TICKETS = [
    TicketCase(
        name="double-charge",
        ticket="""\
Subject: Still broken after your "fix"

This is the third time I'm writing in. My account was charged twice last week and
nobody has refunded me yet. I was told on Monday this would be sorted in 24 hours.
It's Thursday. I need this resolved today or I'm disputing the charges with my bank.
""",
        expect_escalate=True,
        expect_priority="high",
        expect_sentiment="furious",
    ),
    TicketCase(
        name="billing-question",
        ticket="""\
Subject: Quick question about my invoice

Hi, I noticed my invoice this month has a line item labeled "proration" that I don't
recognize. Could someone explain what that charge is for whenever you get a chance?
No rush at all, just curious.
""",
        expect_escalate=False,
        expect_priority="low",
        expect_sentiment="calm",
    ),
    TicketCase(
        name="shipping-delay",
        ticket="""\
Subject: Order still not shipped

My order was supposed to ship three days ago and the tracking page still says
"preparing for shipment". This is the second time an order has been delayed. Can
someone give me an actual update today?
""",
        expect_escalate=False,
        expect_priority="medium",
        expect_sentiment="annoyed",
    ),
    TicketCase(
        name="security-breach",
        ticket="""\
Subject: URGENT - someone logged into my account

I just got an alert that someone logged into my account from a country I've never
been to and changed my password. I can't get back in. There is payment info saved
on this account. I need this locked down right now.
""",
        expect_escalate=True,
        expect_priority="high",
        expect_sentiment="upset",
    ),
]


def _auto_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _closest_level(score: float, levels: list[str]) -> str:
    index = round(min(max(score, 0.0), len(levels) - 1))
    return levels[index]


def _mark(ok: bool) -> str:
    return "match" if ok else "MISMATCH"


def run() -> None:
    print(f"Loading {CHECKPOINT} ...\n")
    engine = load_engine(CHECKPOINT, device=_auto_device())

    passed = 0
    call_times = []
    for i, case in enumerate(TICKETS, start=1):
        start = time.perf_counter()
        response = engine.ask(case.ticket, QUESTIONS)
        elapsed = time.perf_counter() - start
        call_times.append(elapsed)
        answers = response.answers

        actual_escalate = answers["escalate"].noul > 0.5
        actual_priority = answers["priority"].choice
        actual_sentiment = _closest_level(answers["sentiment"].score, SENTIMENT_LEVELS)

        checks = [
            ("escalate", case.expect_escalate, actual_escalate),
            ("priority", case.expect_priority, actual_priority),
            ("sentiment", case.expect_sentiment, actual_sentiment),
        ]
        case_ok = all(expected == actual for _, expected, actual in checks)
        passed += case_ok

        print(f"Ticket {i} ({case.name}): {_mark(case_ok)} ({elapsed:.2f}s)")
        for question, expected, actual in checks:
            print(f"    {question:<10} expected={expected!r:<8} actual={actual!r:<8} {_mark(expected == actual)}")

    print(f"\n{passed}/{len(TICKETS)} tickets fully matched expectations")
    print(f"average call time: {sum(call_times) / len(call_times):.2f}s")
