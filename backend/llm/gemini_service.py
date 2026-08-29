import os
import json

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
# DEFAULT FALLBACK RESPONSE
# ============================================================

def fallback_response(
    explanation="The AI insight could not be generated.",
    uncertainty="The AI service was unavailable or returned an invalid response.",
    recommended_action="Review the available evidence manually before taking action."
):
    return {
        "explanation": explanation,
        "uncertainty": uncertainty,
        "recommended_action": recommended_action
    }


# ============================================================
# CLEAN GEMINI RESPONSE
# ============================================================

def clean_response(response_text: str) -> str:

    if not response_text:
        return ""

    response_text = response_text.strip()

    # Remove Markdown code fences
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
# GENERATE INSIGHT
# ============================================================

def generate_insight(prompt: str) -> dict:

    # --------------------------------------------------------
    # Validate prompt
    # --------------------------------------------------------

    if not prompt or not prompt.strip():

        return fallback_response(
            explanation="No analysis prompt was provided.",
            uncertainty="The AI analysis could not be performed because the prompt was empty.",
            recommended_action="Review the available KPI and driver evidence manually."
        )


    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

        # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    try:

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

    except Exception as error:

        error_text = str(error)

        print(
            f"Gemini API error: {error_text}"
        )

        # ----------------------------------------------------
        # Handle Gemini quota / rate-limit errors
        # ----------------------------------------------------

        if (
            "429" in error_text
            or "quota exceeded" in error_text.lower()
            or "rate limit" in error_text.lower()
        ):

            return fallback_response(
                explanation=(
                    "The verified KPI, driver, and customer "
                    "evidence analysis was completed, but the "
                    "AI explanation is temporarily unavailable "
                    "because the Gemini API quota was exceeded."
                ),
                uncertainty=(
                    "The analytical results remain available. "
                    "However, the AI-generated interpretation "
                    "could not be produced until the Gemini "
                    "API quota resets. Correlations indicate "
                    "association rather than causation."
                ),
                recommended_action=(
                    "Review the verified KPI movement, observed "
                    "drivers, and supporting customer evidence. "
                    "Retry the AI explanation after the Gemini "
                    "quota resets."
                )
            )

        # ----------------------------------------------------
        # Handle other Gemini API errors
        # ----------------------------------------------------

        return fallback_response(
            explanation=(
                "The verified KPI, driver, and customer evidence "
                "analysis was completed, but the AI explanation "
                "could not be generated because the Gemini "
                "service returned an error."
            ),
            uncertainty=(
                "The underlying AI service returned an error. "
                "The analytical results shown by InsightForge "
                "should be reviewed manually."
            ),
            recommended_action=(
                "Review the KPI, driver analysis, and supporting "
                "evidence manually."
            )
        )


    # --------------------------------------------------------
    # Extract response
    # --------------------------------------------------------

    try:

        response_text = interaction.output_text

    except AttributeError:

        return fallback_response(
            explanation="The Gemini service returned an unexpected response.",
            uncertainty="The AI response did not contain the expected output text.",
            recommended_action="Review the available evidence manually."
        )


    # --------------------------------------------------------
    # Validate response
    # --------------------------------------------------------

    response_text = clean_response(
        response_text
    )

    if not response_text:

        return fallback_response(
            explanation="Gemini returned an empty response.",
            uncertainty="No AI-generated explanation was available.",
            recommended_action="Review the available KPI and evidence manually."
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
            )
        )


    # ========================================================
    # VALIDATE JSON OBJECT
    # ========================================================

    if not isinstance(insight, dict):

        return fallback_response(
            explanation="The AI returned an unexpected response structure.",
            uncertainty=(
                "The Gemini response was valid JSON but was "
                "not a JSON object containing the expected fields."
            ),
            recommended_action="Review the available evidence manually."
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


    # --------------------------------------------------------
    # Handle missing explanation
    # --------------------------------------------------------

    if not explanation:

        explanation = (
            "No explanation was generated "
            "for the available evidence."
        )


    # --------------------------------------------------------
    # Handle missing uncertainty
    # --------------------------------------------------------

    if not uncertainty:

        uncertainty = (
            "Uncertainty information was not "
            "provided by the AI response."
        )


    # --------------------------------------------------------
    # Handle missing recommendation
    # --------------------------------------------------------

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
        )
    }