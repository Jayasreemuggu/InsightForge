import pandas as pd


def calculate_driver_contribution(
    driver_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate relative contribution of observed drivers
    to the current KPI movement.

    This is a heuristic attribution measure based on:
    - magnitude of current driver change
    - historical correlation
    - direction alignment

    It does NOT establish causation.
    """

    if driver_df.empty:
        return driver_df.copy()

    result = driver_df.copy()

    result["contribution_weight"] = (
        result["percentage_change"].abs()
        * result["correlation"].abs()
        * result["direction_alignment"].abs()
    )

    total_weight = result["contribution_weight"].sum()

    if total_weight == 0:
        result["contribution_percentage"] = 0.0
    else:
        result["contribution_percentage"] = (
            result["contribution_weight"]
            / total_weight
        ) * 100

    return result