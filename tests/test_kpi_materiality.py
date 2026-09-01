import pandas as pd

from backend.analytics.change_detection import (
    calculate_percentage_change
)

from backend.analytics.anomaly_detection import (
    detect_significant_changes
)


def test_material_kpi_movement_is_detected_and_prioritised():

    df = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-01-01",
            "2025-02-01",
            "2025-03-01"
        ]),
        "region": [
            "North",
            "North",
            "North"
        ],
        "revenue": [
            100000,
            102000,
            120000
        ]
    })

    df = calculate_percentage_change(df)

    result = detect_significant_changes(
        df,
        percentage_threshold=5.0
    )

    march = result[
        result["date"] == pd.Timestamp("2025-03-01")
    ].iloc[0]

    assert march["percentage_change"] > 5.0

    assert bool(march["is_significant"]) is True

    assert march["materiality_score"] > 1.0

    assert march["priority"] in [
        "Medium",
        "High"
    ]