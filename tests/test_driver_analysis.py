import pandas as pd

from backend.analytics.driver_analysis import (
    analyze_driver_changes
)


def test_driver_changes_are_ranked():

    df = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-01-01",
            "2025-02-01",
            "2025-03-01",
            "2025-04-01",
            "2025-05-01",
            "2025-06-01"
        ]),
        "region": [
            "North",
            "North",
            "North",
            "North",
            "North",
            "North"
        ],
        "revenue": [
            100000,
            102000,
            105000,
            108000,
            112000,
            125000
        ],
        "support_resolution_hours": [
            10,
            10.5,
            11,
            11.5,
            12,
            15
        ],
        "product_usage": [
            90,
            89,
            88,
            87,
            86,
            80
        ],
        "renewal_rate": [
            90,
            90,
            91,
            91,
            92,
            93
        ]
    })

    result = analyze_driver_changes(
        df,
        region="North",
        date="2025-06-01"
    )

    assert not result.empty

    assert set(result["driver"]) == {
        "support_resolution_hours",
        "product_usage",
        "renewal_rate"
    }

    assert "driver_score" in result.columns

    assert "correlation" in result.columns

    assert "direction_alignment" in result.columns

    assert "historical_observations" in result.columns

    assert "correlation_p_value" in result.columns

    assert "correlation_significance" in result.columns

    assert result["driver_score"].notna().all()

    assert result["historical_observations"].eq(5).all()

    assert result.iloc[0]["direction_alignment"] >= (
        result.iloc[-1]["direction_alignment"]
    )