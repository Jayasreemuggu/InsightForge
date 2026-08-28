def calculate_confidence(
    kpi_change: float,
    driver_count: int,
    evidence_count: int,
    qualitative_evidence_count: int = 0
) -> str:
    """
    Calculate a qualitative evidence-strength label.

    This is a heuristic for the InsightForge application.
    It is NOT statistical confidence.
    """

    score = 0

    # 1. KPI change magnitude
    if abs(kpi_change) >= 20:
        score += 2
    elif abs(kpi_change) >= 10:
        score += 1

    # 2. Number of observed drivers
    if driver_count >= 3:
        score += 1
    elif driver_count >= 1:
        score += 0.5

    # 3. Total supporting evidence
    if evidence_count >= 4:
        score += 2
    elif evidence_count >= 2:
        score += 1
    elif evidence_count >= 1:
        score += 0.5

    # 4. Qualitative evidence
    if qualitative_evidence_count >= 3:
        score += 2
    elif qualitative_evidence_count >= 1:
        score += 1

    # Convert score into a qualitative label
    if score >= 6:
        return "Strong"

    if score >= 3:
        return "Moderate"

    return "Limited"