from backend.analysis_pipeline import run_analysis


def test_sparse_history_abstention():

    result = run_analysis(
        sales_file="data/sparse_history_abstention.csv",
        feedback_file="data/customer_feedback.csv",
        region="Test",
        date="2025-06-01",
        persona="Executive"
    )

    assert result["abstained"] is True
    assert result["confidence"] == "Low"

    print("ABSTENTION TEST PASSED")
    print("abstained:", result["abstained"])
    print("confidence:", result["confidence"])


if __name__ == "__main__":
    test_sparse_history_abstention()