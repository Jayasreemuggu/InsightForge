from backend.llm.gemini_service import build_telemetry


def test_cost_telemetry_calculation():

    telemetry = build_telemetry(
        latency_ms=1000,
        llm_calls=1,
        input_tokens=1000,
        output_tokens=200,
    )

    expected_cost = (
        (1000 / 1_000_000) * 0.75
        +
        (200 / 1_000_000) * 3.75
    )

    assert telemetry["input_tokens"] == 1000
    assert telemetry["output_tokens"] == 200
    assert telemetry["llm_calls"] == 1

    assert telemetry["estimated_cost"] == expected_cost

    assert telemetry["pricing_currency"] == "USD"
    assert telemetry["input_cost_per_1m_tokens"] == 0.75
    assert telemetry["output_cost_per_1m_tokens"] == 3.75

    print("COST TELEMETRY TEST PASSED")
    print("Estimated cost:", telemetry["estimated_cost"])


if __name__ == "__main__":
    test_cost_telemetry_calculation()