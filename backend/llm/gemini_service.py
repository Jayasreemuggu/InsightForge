import os
import json
import time

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. "
        "Please add GEMINI_API_KEY to the .env file."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=api_key,
    http_options={
        "api_version": "v1"
    }
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# TELEMETRY CONFIGURATION
# ============================================================

# Pricing is intentionally disabled until verified.
INPUT_COST_PER_1M_TOKENS = 0.75
OUTPUT_COST_PER_1M_TOKENS = 3.75


def build_telemetry(
    latency_ms=None,
    llm_calls=0,
    input_tokens=None,
    output_tokens=None,
    estimated_cost=None,
    error=None
):
    """
    Build runtime telemetry for one LLM interaction.
    """

    if (
        estimated_cost is None
        and input_tokens is not None
        and output_tokens is not None
        and INPUT_COST_PER_1M_TOKENS is not None
        and OUTPUT_COST_PER_1M_TOKENS is not None
    ):
        estimated_cost = (
            (input_tokens / 1_000_000)
            * INPUT_COST_PER_1M_TOKENS
            +
            (output_tokens / 1_000_000)
            * OUTPUT_COST_PER_1M_TOKENS
        )

    return {
        "model": MODEL_NAME,
        "latency_ms": latency_ms,
        "llm_calls": llm_calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost": estimated_cost,
        "pricing_currency": "USD",
        "input_cost_per_1m_tokens": INPUT_COST_PER_1M_TOKENS,
        "output_cost_per_1m_tokens": OUTPUT_COST_PER_1M_TOKENS,
        "error": error
    }


# ============================================================
# DEFAULT FALLBACK RESPONSE
# ============================================================

def fallback_response(
    explanation="The AI insight could not be generated.",
    uncertainty=(
        "The AI service was unavailable or returned "
        "an invalid response."
    ),
    recommended_action=(
        "Review the available evidence manually."
    ),
    telemetry=None
):
    """
    Deterministic fallback used whenever the LLM
    cannot safely provide an insight.
    """

    return {
        "explanation": str(explanation),
        "uncertainty": str(uncertainty),
        "recommended_action": str(recommended_action),
        "telemetry": telemetry or build_telemetry(),
        "llm_available": False
    }


# ============================================================
# CLEAN GEMINI RESPONSE
# ============================================================

def clean_response(response_text: str) -> str:

    if not response_text:
        return ""

    response_text = response_text.strip()

    if response_text.startswith("```json"):

        response_text = response_text[
            len("```json"):
        ].strip()

    elif response_text.startswith("```"):

        response_text = response_text[
            len("```"):
        ].strip()

    if response_text.endswith("```"):

        response_text = response_text[
            :-len("```")
        ].strip()

    return response_text


# ============================================================
# EXTRACT TOKEN USAGE
# ============================================================

def extract_usage(interaction):

    input_tokens = None
    output_tokens = None

    usage = getattr(
        interaction,
        "usage",
        None
    )

    if usage is None:
        return input_tokens, output_tokens

    input_tokens = getattr(
        usage,
        "input_tokens",
        None
    )

    output_tokens = getattr(
        usage,
        "output_tokens",
        None
    )

    return input_tokens, output_tokens


# ============================================================
# GENERATE INSIGHT
# ============================================================

def generate_insight(
    prompt: str,
    persona: str = "Executive"
) -> dict:

    persona = str(
        persona
    ).strip().lower()

    persona_instructions = {

        "executive": """
You are generating an executive-level business insight.

Focus on:
- Exact KPI movement and business impact.
- Top 1-3 likely drivers.
- Materiality and priority.
- Customer/business evidence.
- Clear business risk or opportunity.
- One practical recommended action.

Keep the explanation concise and decision-oriented.
Do not overwhelm the executive with statistical details
unless they materially affect confidence.
""",

        "analyst": """
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
""",

        "manager": """
You are generating a manager-level business insight.

Focus on:
- Exact KPI movement.
- Main operational drivers.
- Evidence supporting each driver.
- Which drivers are controllable.
- Practical corrective action.
- Suggested owner or responsible function.
- Expected monitoring metric.
- Confidence and limitations.

Translate analytical findings into operational decisions.
Do not claim causation when only correlation is available.
"""
    }

    persona_instruction = persona_instructions.get(
        persona,
        persona_instructions["executive"]
    )

    # ========================================================
    # BUILD CONTROLLED PROMPT
    # ========================================================

    enhanced_prompt = f"""
{persona_instruction}

GENERAL RULES:

The LLM is NOT the source of quantitative truth.

All numerical values must come from the supplied
analytical evidence.

Do not invent:
- KPI values
- driver values
- correlations
- statistical significance
- customer evidence
- causal relationships
- business events

If evidence is insufficient or contradictory,
explicitly state the limitation and recommend
abstaining or requesting clarification.

Correlation does not imply causation.

Return ONLY valid JSON with exactly these fields:

{{
    "explanation": "...",
    "uncertainty": "...",
    "recommended_action": "..."
}}

PERSONA:
{persona}

ANALYTICAL CONTEXT:
{prompt}
"""

    # ========================================================
    # VALIDATE PROMPT
    # ========================================================

    if not prompt or not prompt.strip():

        return fallback_response(
            explanation=(
                "No analysis prompt was provided."
            ),
            uncertainty=(
                "The AI analysis could not be performed "
                "because the prompt was empty."
            ),
            recommended_action=(
                "Review the available KPI and driver "
                "evidence manually."
            )
        )

    # ========================================================
    # START TIMER
    # ========================================================

    start_time = time.perf_counter()

    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=enhanced_prompt
        )

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        input_tokens, output_tokens = extract_usage(
            interaction
        )

        total_tokens = None

        if (
            input_tokens is not None
            and output_tokens is not None
        ):
            total_tokens = (
                input_tokens
                + output_tokens
            )

        telemetry = build_telemetry(
            latency_ms=round(
                latency_ms,
                2
            ),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            llm_calls=1
        )

        telemetry["total_tokens"] = total_tokens

    except Exception as error:

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        error_text = str(error)

        # ====================================================
        # HANDLE QUOTA / RATE LIMIT
        # ====================================================

        if (
            "429" in error_text
            or "quota exceeded" in error_text.lower()
            or "rate limit" in error_text.lower()
        ):
            print(
                "[GEMINI] Quota/rate limit exceeded. "
                "Using deterministic fallback without retry."
            )
        else:
            print(
                f"Gemini API error: {error_text}"
            )

        telemetry = build_telemetry(
            latency_ms=round(
                latency_ms,
                2
            ),
            input_tokens=None,
            output_tokens=None,
            llm_calls=1,
            error=error_text
        )

        # ====================================================
        # HANDLE QUOTA / RATE LIMIT
        # ====================================================

        if (
            "429" in error_text
            or
            "quota exceeded"
            in error_text.lower()
            or
            "rate limit"
            in error_text.lower()
        ):

            if persona == "analyst":

                fallback_explanation = (
                    "The verified KPI, driver, and customer "
                    "evidence analysis was completed, but Gemini "
                    "was unavailable because the API quota was "
                    "exceeded. The analytical results should be "
                    "interpreted using the ranked drivers, "
                    "percentage changes, correlations, and "
                    "statistical significance already calculated."
                )

                fallback_action = (
                    "Review the ranked driver statistics and "
                    "validate the strongest associations using "
                    "additional historical observations or "
                    "causal analysis before drawing causal "
                    "conclusions."
                )

            elif persona == "manager":

                fallback_explanation = (
                    "The verified KPI, driver, and customer "
                    "evidence analysis was completed, but Gemini "
                    "was unavailable because the API quota was "
                    "exceeded. Focus on the observed operational "
                    "drivers and the customer evidence supporting "
                    "them."
                )

                fallback_action = (
                    "Prioritize investigation of the controllable "
                    "operational drivers, assign responsible teams, "
                    "and monitor the affected KPI and driver metrics."
                )

            else:

                fallback_explanation = (
                    "The verified KPI, driver, and customer "
                    "evidence analysis was completed, but Gemini "
                    "was unavailable because the API quota was "
                    "exceeded. The verified KPI movement and "
                    "observed drivers remain available for "
                    "decision-making."
                )

                fallback_action = (
                    "Review the verified KPI movement and "
                    "highest-ranked drivers, then prioritize "
                    "the most material business issue while "
                    "monitoring the KPI for recovery."
                )

            return fallback_response(
                explanation=fallback_explanation,
                uncertainty=(
                    "The analytical results remain available. "
                    "The AI-generated interpretation could not "
                    "be produced because the Gemini API quota "
                    "was exceeded. Correlations indicate "
                    "association rather than causation, and "
                    "historical correlation reliability may "
                    "be limited."
                ),
                recommended_action=fallback_action,
                telemetry=telemetry
            )

        # ====================================================
        # HANDLE OTHER API ERRORS
        # ====================================================

        return fallback_response(
            explanation=(
                "The verified KPI, driver, and customer "
                "evidence analysis was completed, but the "
                "AI explanation could not be generated because "
                "the Gemini service returned an error."
            ),
            uncertainty=(
                "The underlying AI service returned an error. "
                "The analytical results shown by InsightForge "
                "should be reviewed manually."
            ),
            recommended_action=(
                "Review the KPI, driver analysis, and "
                "supporting evidence manually."
            ),
            telemetry=telemetry
        )

    # ========================================================
    # EXTRACT RESPONSE TEXT
    # ========================================================

    try:

        response_text = interaction.output_text

    except AttributeError:

        return fallback_response(
            explanation=(
                "The Gemini service returned an "
                "unexpected response."
            ),
            uncertainty=(
                "The AI response did not contain the "
                "expected output text."
            ),
            recommended_action=(
                "Review the available evidence manually."
            ),
            telemetry=telemetry
        )

    # ========================================================
    # CLEAN RESPONSE
    # ========================================================

    response_text = clean_response(
        response_text
    )

    if not response_text:

        return fallback_response(
            explanation=(
                "Gemini returned an empty response."
            ),
            uncertainty=(
                "No AI-generated explanation "
                "was available."
            ),
            recommended_action=(
                "Review the available KPI and "
                "evidence manually."
            ),
            telemetry=telemetry
        )

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        insight = json.loads(
            response_text
        )

    except json.JSONDecodeError:

        return fallback_response(
            explanation=response_text,
            uncertainty=(
                "The AI response was not returned in "
                "the expected JSON format. The explanation "
                "is shown as plain text and should be "
                "reviewed manually."
            ),
            recommended_action=(
                "Review the supplied KPI, driver analysis, "
                "and supporting evidence before taking action."
            ),
            telemetry=telemetry
        )

    # ========================================================
    # VALIDATE JSON OBJECT
    # ========================================================

    if not isinstance(
        insight,
        dict
    ):

        return fallback_response(
            explanation=(
                "The AI returned an unexpected "
                "response structure."
            ),
            uncertainty=(
                "The Gemini response was valid JSON but "
                "was not a JSON object containing the "
                "expected fields."
            ),
            recommended_action=(
                "Review the available evidence manually."
            ),
            telemetry=telemetry
        )

    # ========================================================
    # EXTRACT EXPECTED FIELDS
    # ========================================================

    explanation = insight.get(
        "explanation"
    )

    uncertainty = insight.get(
        "uncertainty"
    )

    recommended_action = insight.get(
        "recommended_action"
    )

    if not explanation:

        explanation = (
            "No explanation was generated "
            "for the available evidence."
        )

    if not uncertainty:

        uncertainty = (
            "Uncertainty information was not "
            "provided by the AI response."
        )

    if not recommended_action:

        recommended_action = (
            "Review the available evidence "
            "before taking action."
        )

    # ========================================================
    # RETURN STRUCTURED RESULT
    # ========================================================

    return {
        "explanation": str(
            explanation
        ),
        "uncertainty": str(
            uncertainty
        ),
        "recommended_action": str(
            recommended_action
        ),
        "telemetry": telemetry,
        "llm_available": True
    }