import pandas as pd

from backend.reconciliation import reconcile_sources


def test_heterogeneous_sources_are_reconciled():

    sales_df = pd.read_csv("data/sales.csv")
    feedback_df = pd.read_csv("data/customer_feedback.csv")

    result = reconcile_sources(
        sales_df=sales_df,
        feedback_df=feedback_df,
        region="North",
        date="2025-06-01"
    )

    # Basic validation
    assert result["reconciliation_status"] == "reconciled"

    # Verify common investigation key
    assert result["investigation_key"]["region"] == "North"
    assert result["investigation_key"]["period"] == "2025-06"

    # Verify monthly + region alignment
    assert (
        result["investigation_key"]["alignment_grain"]
        == "Monthly + Region"
    )

    # Verify multiple heterogeneous sources were considered
    assert len(result["sources"]) >= 3

    # Every source should have alignment information
    for source in result["sources"]:
        assert "source_grain" in source
        assert "analysis_grain" in source
        assert "aligned" in source

    print("\n========== RECONCILIATION TEST ==========")
    print("Status:", result["reconciliation_status"])
    print("Investigation key:", result["investigation_key"])
    print("Sources:", len(result["sources"]))

    for source in result["sources"]:
        print(
            f"- {source['source']}: "
            f"grain={source['source_grain']}, "
            f"analysis_grain={source['analysis_grain']}, "
            f"aligned={source['aligned']}"
        )

    print("==========================================")


if __name__ == "__main__":
    test_heterogeneous_sources_are_reconciled()
    print("\nTEST PASSED")