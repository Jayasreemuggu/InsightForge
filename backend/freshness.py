import pandas as pd


def check_source_freshness(
    source_name: str,
    df: pd.DataFrame,
    investigation_date: str
):
    """
    Check whether a source contains data for the
    requested investigation month.

    Status:
    - Fresh: source contains data for investigation month
    - Stale: source's latest data is older than investigation month
    - Unavailable: source has no usable date information
    """

    investigation_date = pd.to_datetime(
        investigation_date
    )

    if df is None or df.empty:
        return {
            "source": source_name,
            "latest_data_date": None,
            "investigation_period": investigation_date.strftime("%Y-%m"),
            "freshness_status": "Unavailable"
        }

    if "date" not in df.columns:
        return {
            "source": source_name,
            "latest_data_date": None,
            "investigation_period": investigation_date.strftime("%Y-%m"),
            "freshness_status": "Unavailable"
        }

    dates = pd.to_datetime(
        df["date"],
        errors="coerce"
    ).dropna()

    if dates.empty:
        return {
            "source": source_name,
            "latest_data_date": None,
            "investigation_period": investigation_date.strftime("%Y-%m"),
            "freshness_status": "Unavailable"
        }

    latest_date = dates.max()

    investigation_period = investigation_date.to_period("M")
    latest_period = latest_date.to_period("M")

    if latest_period >= investigation_period:
        status = "Fresh"
    else:
        status = "Stale"

    return {
        "source": source_name,
        "latest_data_date": latest_date.strftime("%Y-%m-%d"),
        "investigation_period": investigation_period.strftime("%Y-%m"),
        "freshness_status": status
    }