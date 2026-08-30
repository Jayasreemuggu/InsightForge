import pandas as pd

from backend.analytics.contribution import (
    calculate_driver_contribution
)


def test_driver_contribution():

    drivers = pd.DataFrame([
        {
            "driver": "product_usage",
            "percentage_change": -18.60,
            "correlation": 0.998,
            "direction_alignment": 1
        },
        {
            "driver": "renewal_rate",
            "percentage_change": -11.83,
            "correlation": 0.965,
            "direction_alignment": 1
        }
    ])

    result = calculate_driver_contribution(drivers)

    assert "contribution_weight" in result.columns
    assert "contribution_percentage" in result.columns

    total = result["contribution_percentage"].sum()

    assert abs(total - 100.0) < 0.001
    assert (result["contribution_percentage"] >= 0).all()
    assert (result["contribution_percentage"] <= 100).all()

    print("\n========== CONTRIBUTION TEST ==========")
    print(
        result[
            [
                "driver",
                "contribution_weight",
                "contribution_percentage"
            ]
        ].to_string(index=False)
    )

    print(f"\nTotal contribution: {total:.2f}%")
    print("TEST PASSED")


if __name__ == "__main__":
    test_driver_contribution()