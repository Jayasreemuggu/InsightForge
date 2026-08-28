def build_insight_context(
    region,
    date,
    kpi_change,
    drivers,
    evidence
):
    return {
        "region": region,
        "date": date,
        "kpi_change": kpi_change,
        "drivers": drivers,
        "evidence": evidence
    }