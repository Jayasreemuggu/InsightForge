import pandas as pd

from backend.reconciliation import reconcile_sources


def test_heterogeneous_sources_are_reconciled():

    sales_df = pd.read_csv(
        "data/sales.csv"
    )

    feedback_df = pd.read_csv(
        "data/customer_feedback.csv"
    )

    product_usage_df = pd.read_csv(
        "data/product_usage.csv"
    )

    renewal_df = pd.read_csv(
        "data/renewal_data.csv"
    )

    support_tickets_df = pd.read_csv(
        "data/support_tickets.csv"
    )

    result = reconcile_sources(
        sales_df=sales_df,
        feedback_df=feedback_df,
        product_usage_df=product_usage_df,
        renewal_df=renewal_df,
        support_tickets_df=support_tickets_df,
        region="North",
        date="2025-06-01"
    )

    assert "sources" in result
    assert "reconciliation_status" in result
    assert "source_freshness" in result

    assert len(result["sources"]) == 5

    source_names = [
        source["source"]
        for source in result["sources"]
    ]

    assert "Sales / KPI data" in source_names
    assert "Product usage data" in source_names
    assert "Renewal data" in source_names
    assert "Support ticket data" in source_names
    assert "Customer feedback" in source_names