import time


# Gemini 3.6 Flash introductory pricing
# Valid through December 31, 2026.
INPUT_COST_PER_1M_TOKENS = 0.75
OUTPUT_COST_PER_1M_TOKENS = 3.75


def extract_usage_metadata(response):
    """
    Extract token usage from different Gemini/API response formats.

    Returns None values when the provider does not expose usage metadata.
    """

    usage = getattr(response, "usage_metadata", None)

    if usage is not None:

        prompt_tokens = getattr(
            usage,
            "prompt_token_count",
            None
        )

        output_tokens = getattr(
            usage,
            "candidates_token_count",
            None
        )

        total_tokens = getattr(
            usage,
            "total_token_count",
            None
        )

        return {
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }

    # OpenAI-compatible fallback
    usage = getattr(response, "usage", None)

    if usage is not None:

        prompt_tokens = getattr(
            usage,
            "prompt_tokens",
            None
        )

        output_tokens = getattr(
            usage,
            "completion_tokens",
            None
        )

        total_tokens = getattr(
            usage,
            "total_tokens",
            None
        )

        return {
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }

    return {
        "prompt_tokens": None,
        "output_tokens": None,
        "total_tokens": None
    }


def calculate_estimated_cost(
    prompt_tokens,
    output_tokens
):
    """
    Estimate LLM cost using the configured Gemini pricing.

    Returns 0 when token usage is unavailable.
    """

    if prompt_tokens is None:
        prompt_tokens = 0

    if output_tokens is None:
        output_tokens = 0

    input_cost = (
        prompt_tokens / 1_000_000
    ) * INPUT_COST_PER_1M_TOKENS

    output_cost = (
        output_tokens / 1_000_000
    ) * OUTPUT_COST_PER_1M_TOKENS

    return round(
        input_cost + output_cost,
        6
    )


def build_llm_telemetry(
    model,
    started_at,
    response=None,
    success=True
):

    latency = time.perf_counter() - started_at

    usage = extract_usage_metadata(response)

    estimated_cost = calculate_estimated_cost(
        usage["prompt_tokens"],
        usage["output_tokens"]
    )

    return {
        "model": model,
        "model_calls": 1,
        "success": success,
        "latency_seconds": round(
            latency,
            4
        ),
        "prompt_tokens": usage[
            "prompt_tokens"
        ],
        "output_tokens": usage[
            "output_tokens"
        ],
        "total_tokens": usage[
            "total_tokens"
        ],
        "estimated_cost_usd": estimated_cost
    }