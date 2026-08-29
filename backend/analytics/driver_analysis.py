import pandas as pd
from scipy.stats import pearsonr

def analyze_drivers(
    df: pd.DataFrame,
    target: str = "revenue"
) -> pd.DataFrame:

    numeric_columns = df.select_dtypes(include="number").columns
    driver_columns = [col for col in numeric_columns if col != target]

    results = []

    for driver in driver_columns:
        correlation = df[target].corr(df[driver])

        if pd.isna(correlation):
            correlation = 0.0

        results.append({
            "driver": driver,
            "correlation": correlation,
            "abs_correlation": abs(correlation)
        })

    if not results:
        return pd.DataFrame(
            columns=[
                "driver",
                "correlation",
                "abs_correlation"
            ]
        )

    return (
        pd.DataFrame(results)
        .sort_values(
            "abs_correlation",
            ascending=False
        )
        .reset_index(drop=True)
    )


def analyze_driver_changes(
    df: pd.DataFrame,
    region: str,
    date: str,
    target: str = "revenue"
) -> pd.DataFrame:

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    target_date = pd.to_datetime(date)

    region_df = (
        df[df["region"] == region]
        .sort_values("date")
        .copy()
    )

    current = region_df[
        region_df["date"] == target_date
    ]

    previous = region_df[
        region_df["date"] < target_date
    ]

    if current.empty or previous.empty:
        return pd.DataFrame(
            columns=[
                "driver",
                "previous_value",
                "current_value",
                "percentage_change",
                "correlation",
                "direction_alignment",
                "driver_score",
                "historical_observations",
                "correlation_reliability",
                "correlation_p_value",
                "correlation_significance"
            ]
        )

    current_row = current.iloc[0]
    previous_row = previous.iloc[-1]

    # Revenue change for the investigated period
    previous_revenue = previous_row[target]
    current_revenue = current_row[target]

    if previous_revenue == 0:
        revenue_change = 0.0
    else:
        revenue_change = (
            (current_revenue - previous_revenue)
            / previous_revenue
        ) * 100

        # ====================================================
    # Define business drivers
    # ====================================================
    #
    # Only variables intended to explain revenue movement
    # are treated as drivers.
    #
    # Orders is excluded because it is an operational KPI
    # closely tied to revenue rather than an independent
    # explanatory driver.
    #

    driver_columns = [
        "support_resolution_hours",
        "product_usage",
        "renewal_rate"
    ]

    # Keep only drivers that actually exist in the dataset.
    driver_columns = [
        col
        for col in driver_columns
        if col in region_df.columns
    ]

    results = []

    for driver in driver_columns:

        previous_value = previous_row[driver]
        current_value = current_row[driver]

        # Month-over-month driver change
        if previous_value == 0:
            percentage_change = 0.0
        else:
            percentage_change = (
                (current_value - previous_value)
                / previous_value
            ) * 100

        # Historical association with revenue.
        # Only data before the investigated period is used
        # to avoid using future observations.
        historical = previous[
            [target, driver]
        ].dropna()

        historical_observations = len(historical)

        if len(historical) >= 3:
            correlation, correlation_p_value = pearsonr(
                historical[target],
                historical[driver]
            )
        else:
            correlation = 0.0
            correlation_p_value = 1.0

        if pd.isna(correlation):
            correlation = 0.0

        if pd.isna(correlation_p_value):
            correlation_p_value = 1.0
        
        if historical_observations < 5:
            correlation_reliability = "Very Limited"
        elif historical_observations < 10:
            correlation_reliability = "Limited"
        else:
            correlation_reliability = "Moderate"

        # Statistical significance should only be treated as
        # meaningful when enough historical observations exist.
        #
        # With fewer than 10 observations, the correlation may
        # appear significant but is not considered reliable enough
        # for InsightForge's evidence assessment.

        if correlation_p_value < 0.05:
            correlation_significance = "Statistically significant"
        else:
            correlation_significance = "Not statistically significant"

        # Check whether the driver movement is directionally
        # consistent with its historical relationship with revenue.
        expected_revenue_direction = (
            percentage_change * correlation
        )

        if revenue_change == 0 or expected_revenue_direction == 0:
            direction_alignment = 0
        elif (
            expected_revenue_direction > 0
            and revenue_change > 0
        ):
            direction_alignment = 1
        elif (
            expected_revenue_direction < 0
            and revenue_change < 0
        ):
            direction_alignment = 1
        else:
            direction_alignment = 0

        # Transparent association score:
        # magnitude of current change × historical association.
        # ====================================================
        # Driver score
        # ====================================================
        #
        # Combine:
        # 1. Current driver movement
        # 2. Historical correlation
        # 3. Statistical significance
        # 4. Historical sample-size reliability
        #
        # This prevents a very strong correlation based on
        # only a few observations from dominating the ranking.
        #

        if historical_observations >= 10 and correlation_p_value < 0.05:
            significance_weight = 1.0
        elif historical_observations >= 10 and correlation_p_value < 0.10:
            significance_weight = 0.75
        else:
            significance_weight = 0.5

        if historical_observations >= 12:
            sample_weight = 1.0
        elif historical_observations >= 10:
            sample_weight = 0.9
        elif historical_observations >= 5:
            sample_weight = 0.7
        else:
            sample_weight = 0.4

        driver_score = (
            abs(percentage_change)
            * abs(correlation)
            * significance_weight
            * sample_weight
        )

        results.append({
            "driver": driver,
            "previous_value": previous_value,
            "current_value": current_value,
            "percentage_change": percentage_change,
            "correlation": correlation,
            "direction_alignment": direction_alignment,
            "driver_score": driver_score,
            "historical_observations": historical_observations,
            "correlation_reliability": correlation_reliability,
            "correlation_p_value": correlation_p_value,
            "correlation_significance": correlation_significance
        })

    return (
        pd.DataFrame(results)
        .sort_values(
            ["direction_alignment", "driver_score"],
            ascending=[False, False]
        )
        .reset_index(drop=True)
    )