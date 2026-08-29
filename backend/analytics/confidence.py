def calculate_confidence(
    kpi_change: float,
    driver_count: int,
    evidence_count: int,
    qualitative_evidence_count: int = 0,
    historical_observations: int = 0
) -> str:
    """
    Calculate a qualitative evidence-strength label.

    This is a heuristic for the InsightForge application.
    It is NOT statistical confidence.

    Historical sample size is used as a reliability constraint
    so that strong-looking correlations based on very little
    historical data do not automatically produce a Strong label.
    """

    score = 0

    # ========================================================
    # 1. KPI change magnitude
    # ========================================================

    if abs(kpi_change) >= 20:
        score += 2
    elif abs(kpi_change) >= 10:
        score += 1

    # ========================================================
    # 2. Number of observed drivers
    # ========================================================

    if driver_count >= 3:
        score += 1
    elif driver_count >= 1:
        score += 0.5

    # ========================================================
    # 3. Supporting customer evidence
    # ========================================================

    if evidence_count >= 4:
        score += 2
    elif evidence_count >= 2:
        score += 1
    elif evidence_count >= 1:
        score += 0.5

    # ========================================================
    # 4. Qualitative evidence coverage
    # ========================================================

    if qualitative_evidence_count >= 3:
        score += 2
    elif qualitative_evidence_count >= 1:
        score += 1

    # ========================================================
    # 5. Historical-data reliability constraint
    # ========================================================
    #
    # This does NOT pretend to calculate statistical confidence.
    # It prevents a Strong label when driver relationships are
    # based on very little historical data.
    #

    if historical_observations < 5:

        # Very little historical information.
        # Cap the result at Limited.
        return "Limited"

    elif historical_observations < 10:

        # Some historical information exists, but it is still
        # insufficient for a strong reliability assessment.
        if score >= 3:
            return "Moderate"

        return "Limited"

    # ========================================================
    # 6. Final qualitative classification
    # ========================================================

    if score >= 6:
        return "Strong"

    if score >= 3:
        return "Moderate"

    return "Limited"