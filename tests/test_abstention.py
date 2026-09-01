from backend.analysis_pipeline import run_analysis


def test_sparse_history_abstention():

    result = run_analysis(
        sales_file="data/sparse_history_abstention.csv",
        feedback_file="data/customer_feedback.csv",
        region="Test",
        date="2025-06-01",
        persona="Executive"
    )

    # Abstention state
    assert result["abstained"] is True
    assert result["confidence"] == "Low"

    # Analytical results should still be available
    assert "kpi_change" in result
    assert "drivers" in result

    # At least one driver must have insufficient history
    assert any(
        driver.get("historical_observations", 0) < 3
        for driver in result["drivers"]
    )

    # System must communicate uncertainty
    assert result["uncertainty"]
    assert isinstance(result["uncertainty"], str)

    # System must provide a safe next action
    assert result["recommended_action"]
    assert isinstance(result["recommended_action"], str)


if __name__ == "__main__":
    test_sparse_history_abstention()