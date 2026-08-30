import json


def build_insight_context(
    region,
    date,
    kpi_change,
    drivers,
    evidence,
    persona="Executive"
):
    """
    Build the structured context passed to the LLM.

    Quantitative truth comes from deterministic/statistical
    analysis. The LLM is only responsible for interpretation
    and narrative generation.
    """

    return {
        "region": region,
        "date": date,
        "kpi_change": kpi_change,
        "drivers": drivers,
        "evidence": evidence,
        "persona": persona
    }


def build_persona_instructions(persona):
    """
    Return instructions controlling the level and style
    of the generated insight.
    """

    persona = str(persona).strip().lower()

    if persona == "executive":
        return """
You are generating an executive business insight.

Focus on:
1. What changed.
2. Business impact.
3. The top 1-3 evidence-supported drivers.
4. What management should do next.

Keep the explanation concise and decision-oriented.
Do not overwhelm the executive with statistical details.

Do not claim causation unless the supplied evidence explicitly
supports causation.
"""

    if persona == "analyst":
        return """
You are generating an analyst-level business insight.

Focus on:
1. Exact KPI movement.
2. Ranked drivers.
3. Driver percentage changes.
4. Correlations and statistical significance when available.
5. Supporting customer evidence.
6. Limitations and uncertainty.
7. Recommended analytical follow-up.

Preserve important quantitative details.
Explicitly distinguish correlation from causation.
"""

    if persona == "manager":
        return """
You are generating a manager-level business insight.

Focus on:
1. KPI movement.
2. Main operational drivers.
3. Customer/business evidence.
4. Practical actions that can be taken by the team.
5. Risks and uncertainty.

Keep the explanation practical and moderately detailed.
"""

    return """
Generate a concise business insight using only the supplied evidence.
Do not invent facts.
Do not claim causation from correlation.
"""


def build_prompt(
    region,
    date,
    kpi_change,
    drivers,
    evidence,
    persona="Executive"
):
    """
    Construct the prompt for Gemini.

    The prompt explicitly tells the LLM that the analytical
    layer has already established the quantitative results.
    """

    context = build_insight_context(
        region=region,
        date=date,
        kpi_change=kpi_change,
        drivers=drivers,
        evidence=evidence,
        persona=persona
    )

    persona_instructions = build_persona_instructions(
        persona
    )

    return f"""
{persona_instructions}

IMPORTANT RULES:

- The supplied KPI values and analytical results are the
  quantitative source of truth.
- Do not recalculate or invent KPI values.
- Do not invent drivers.
- Do not invent customer evidence.
- Correlation does not prove causation.
- If evidence is weak, explicitly state that confidence is limited.
- If evidence is contradictory, state the contradiction.
- If evidence is insufficient, recommend further investigation.

Return ONLY valid JSON with exactly these fields:

{{
  "explanation": "string",
  "uncertainty": "string",
  "recommended_action": "string"
}}

ANALYTICAL CONTEXT:

{json.dumps(context, indent=2, default=str)}
"""