def get_llm_non_llm_breakdown():
    """
    Describe which parts of InsightForge are deterministic
    and which parts use the LLM.

    Numerical business calculations remain deterministic.
    Gemini is used only for natural-language interpretation.
    """

    non_llm_components = [
        "KPI calculation",
        "Percentage change",
        "Anomaly detection",
        "Regional comparison",
        "Driver analysis",
        "Correlation analysis",
        "Statistical significance",
        "Driver scoring",
        "Contribution calculation",
        "Evidence matching and ranking",
        "Confidence calculation",
        "Source reconciliation",
        "Source freshness",
        "Role-based entitlement filtering"
    ]

    llm_components = [
        "Explanation generation",
        "Uncertainty interpretation",
        "Recommended action generation"
    ]

    return {
        "non_llm": {
            "component_count": len(non_llm_components),
            "components": non_llm_components
        },
        "llm": {
            "component_count": len(llm_components),
            "components": llm_components
        }
    }