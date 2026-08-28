import pandas as pd


def detect_significant_changes(
    df: pd.DataFrame,
    threshold: float = 5.0
) -> pd.DataFrame:
    df = df.copy()

    df["is_significant"] = (
        df["percentage_change"].abs() >= threshold
    )

    return df