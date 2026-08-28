import pandas as pd


def calculate_percentage_change(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["percentage_change"] = (
        df.groupby("region")["revenue"]
        .pct_change() * 100
    )

    return df