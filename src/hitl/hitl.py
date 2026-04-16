"""
Lab 11 — Part 4: Human-in-the-Loop Design
  TODO 12: Confidence Router
  TODO 13: Design 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# TODO 12: Implement ConfidenceRouter
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        # TODO 12: Route based on risk level, then confidence.

        # Rule 1 — High-risk action: always escalate, regardless of confidence.
        # A model can be 99% confident but a human must still authorise money transfers
        # or account deletions — the cost of an incorrect AI decision is too high.
        if action_type in HIGH_RISK_ACTIONS:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason=f"High-risk action requiring human authorisation: {action_type}",
                priority="high",
                requires_human=True,
            )

        # Rule 2 — High confidence: safe to auto-send without human review.
        if confidence >= self.HIGH_THRESHOLD:
            return RoutingDecision(
                action="auto_send",
                confidence=confidence,
                reason="High confidence — response sent automatically",
                priority="low",
                requires_human=False,
            )

        # Rule 3 — Medium confidence: queue for asynchronous human review.
        # The response is shown to the user immediately but flagged for later audit.
        if confidence >= self.MEDIUM_THRESHOLD:
            return RoutingDecision(
                action="queue_review",
                confidence=confidence,
                reason="Medium confidence — queued for human review",
                priority="normal",
                requires_human=True,
            )

        # Rule 4 — Low confidence: escalate to human before responding.
        # The user is informed there will be a short delay for quality assurance.
        return RoutingDecision(
            action="escalate",
            confidence=confidence,
            reason="Low confidence — escalating to human agent immediately",
            priority="high",
            requires_human=True,
        )


# ============================================================
# TODO 13: Design 3 HITL decision points
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "name": "Large Transaction Authorisation",
        # Trigger: any transfer or payment above 50 million VND.
        # At this scale, an incorrect AI decision (wrong account, typo in amount)
        # causes irreversible financial harm that cannot easily be undone.
        "trigger": (
            "Customer requests a transfer, payment, or withdrawal exceeding 50,000,000 VND "
            "(~2,000 USD). Also triggered when destination account is flagged by the "
            "fraud-detection system or is a first-time recipient for this customer."
        ),
        # Human-as-tiebreaker: the AI drafts the transaction summary and proposed
        # action, but a human officer must click Approve/Reject before execution.
        "hitl_model": "human-as-tiebreaker",
        "context_needed": (
            "Full transaction details (sender, receiver, amount, purpose), "
            "customer's last 3 large transactions for pattern comparison, "
            "fraud-risk score from the detection engine, and any recent account "
            "alerts or holds."
        ),
        "example": (
            "Customer types: 'Transfer 200 million VND to account 1234567890 at Techcombank — "
            "this is for a property deposit.' The AI validates the request, checks the fraud "
            "score (medium risk — first-time large transfer), and routes to a human officer "
            "who reviews and approves within 2 minutes before the transfer is executed."
        ),
    },
    {
        "id": 2,
        "name": "Account Modification & Identity Verification",
        # Trigger: requests to change phone number, email, address, or close account.
        # These are irreversible or hard-to-reverse actions that can be exploited
        # by fraudsters to take over a customer's account.
        "trigger": (
            "Customer requests to: close account, change registered phone number or email, "
            "update residential address, or reset 2FA device. Also triggered when AI "
            "confidence in customer identity is below 0.85 (ambiguous ID verification)."
        ),
        # Human-in-the-loop: AI cannot send the confirmation or execute the change
        # until a human agent has verified the customer's identity via callback or video.
        "hitl_model": "human-in-the-loop",
        "context_needed": (
            "Customer KYC documents on file, last successful authentication method and time, "
            "current request details (what is being changed and to what), recent login "
            "history (IP addresses, devices), and any pending or recently executed "
            "sensitive changes."
        ),
        "example": (
            "Customer asks to change registered phone number from 0901234567 to 0987654321. "
            "The AI recognises this as a sensitive modification and pauses the conversation. "
            "A human agent calls the customer on the OLD number to verify intent before "
            "the AI sends the OTP to the new number and completes the change."
        ),
    },
    {
        "id": 3,
        "name": "Loan & Credit Decision Advisory",
        # Trigger: customer asks for loan eligibility, credit limit increases, or
        # when the AI's credit-scoring confidence is below the approval threshold.
        # AI can pre-assess but must not make final credit decisions autonomously
        # due to regulatory requirements and fairness obligations.
        "trigger": (
            "Customer requests: loan application status, credit card limit increase, "
            "or pre-qualification for any credit product. Also triggered when the "
            "AI's automated scoring produces a borderline result (score 580–650 on "
            "a 300–850 scale) where manual underwriting is required by policy."
        ),
        # Human-on-the-loop: AI provides a detailed recommendation report, but a
        # loan officer reviews all decisions asynchronously within 24 hours.
        # Rejected applications are reviewed again before the customer is notified.
        "hitl_model": "human-on-the-loop",
        "context_needed": (
            "Customer credit profile (score, history, existing obligations), income "
            "verification documents, requested loan amount and purpose, AI's risk "
            "assessment breakdown, and regulatory flags (e.g., stressed DTI ratio). "
            "Reviewer also sees comparable approved/rejected profiles for consistency."
        ),
        "example": (
            "Customer applies for a 500M VND home loan. AI runs credit scoring: score 620 "
            "(borderline), DTI 42% (above 40% threshold), employment 18 months (below "
            "24-month preference). AI generates a 'conditional approval' recommendation "
            "and flags it for a loan officer. The officer reviews within 4 hours, "
            "requests additional salary documents, and makes the final decision — "
            "the customer is notified only after human sign-off."
        ),
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Conf':<6} {'Action Type':<18} {'Decision':<15} {'Priority':<10} {'Human?'}")
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<25} {conf:<6.2f} {action_type:<18} "
            f"{decision.action:<15} {decision.priority:<10} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['name']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point['context_needed']}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()
