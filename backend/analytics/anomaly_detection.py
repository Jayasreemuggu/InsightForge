import pandas as pd


def detect_significant_changes(
    df: pd.DataFrame,
    percentage_threshold: float = 5.0,
    absolute_threshold: float | None = None
) -> pd.DataFrame:
    df = df.copy()

    absolute_change = (
        df.groupby("region")["revenue"]
        .diff()
        .abs()
    )

    percentage_material = (
        df["percentage_change"].abs() >= percentage_threshold
    )

    if absolute_threshold is not None:
        absolute_material = (
            absolute_change >= absolute_threshold
        )
    else:
        absolute_material = False

    df["is_significant"] = (
        percentage_material | absolute_material
    )

    # Priority relative to the governed percentage threshold.
    # Higher values = more material movement.
    df["materiality_score"] = (
        df["percentage_change"].abs()
        / percentage_threshold
    )

    # Escalate movements that also exceed the absolute threshold.
    if absolute_threshold is not None:
        absolute_ratio = (
            absolute_change / absolute_threshold
        )

        df["materiality_score"] = (
            df["materiality_score"]
            + absolute_ratio
        )

    df["priority"] = pd.cut(
        df["materiality_score"],
        bins=[-float("inf"), 1, 2, float("inf")],
        labels=["Low", "Medium", "High"]
    )

    return df