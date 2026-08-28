import pandas as pd


def calculate_monthly_revenue(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    df["date"] = pd.to_datetime(df["date"])

    monthly_revenue = (
        df.groupby(["date", "region"])["revenue"]
        .sum()
        .reset_index()
        .sort_values(["region", "date"])
    )

    return monthly_revenue