from guardrail.policy import Policy


def decide(matched: bool, policy: Policy) -> str:
    if not matched:
        return "allow"
    return "block" if policy.mode == "enforce" else "warn"
