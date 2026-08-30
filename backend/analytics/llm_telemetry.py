import time


def extract_usage_metadata(response):
    """
    Extract token usage from different Gemini/API response formats.

    Returns None when the provider does not expose usage metadata.
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


def build_llm_telemetry(
    model,
    started_at,
    response=None,
    success=True
):
    latency = time.perf_counter() - started_at

    usage = extract_usage_metadata(response)

    return {
        "model": model,
        "model_calls": 1,
        "success": success,
        "latency_seconds": round(latency, 4),
        "prompt_tokens": usage["prompt_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"]
    }