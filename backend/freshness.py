import pandas as pd


def check_source_freshness(
    source_name: str,
    df: pd.DataFrame,
    investigation_date: str,
    region: str = None
):
    """
    Check whether a source contains data for the
    requested investigation month and region.

    Status:
    - Fresh: source contains data for investigation month
    - Stale: source's latest regional data is older
      than the investigation month
    - Unavailable: source has no usable data
    """

    investigation_date = pd.to_datetime(
        investigation_date
    )

    investigation_period = (
        investigation_date.to_period("M")
    )

    # --------------------------------------------------
    # Empty source
    # --------------------------------------------------

    if df is None or df.empty:
        return {
            "source": source_name,
            "latest_data_date": None,
            "investigation_period": investigation_period.strftime(
                "%Y-%m"
            ),
            "freshness_status": "Unavailable",
            "region": region
        }

    # --------------------------------------------------
    # Date column validation
    # --------------------------------------------------

    if "date" not in df.columns:
        return {
            "source": source_name,
            "latest_data_date": None,
            "investigation_period": investigation_period.strftime(
                "%Y-%m"
            ),
            "freshness_status": "Unavailable",
            "region": region
        }

    # --------------------------------------------------
    # Normalize dates
    # --------------------------------------------------

    working_df = df.copy()

    working_df["date"] = pd.to_datetime(
        working_df["date"],
        errors="coerce"
    )

    # --------------------------------------------------
    # Restrict freshness check to requested region
    # --------------------------------------------------

    if region is not None and "region" in working_df.columns:

        regional_df = working_df[
            working_df["region"] == region
        ].copy()

        if regional_df.empty:
            return {
                "source": source_name,
                "latest_data_date": None,
                "investigation_period": investigation_period.strftime(
                    "%Y-%m"
                ),
                "freshness_status": "Unavailable",
                "region": region
            }

        working_df = regional_df

    # --------------------------------------------------
    # Remove invalid dates
    # --------------------------------------------------

    dates = (
        working_df["date"]
        .dropna()
    )

    if dates.empty:
        return {
            "source": source_name,
            "latest_data_date": None,
            "investigation_period": investigation_period.strftime(
                "%Y-%m"
            ),
            "freshness_status": "Unavailable",
            "region": region
        }

    # --------------------------------------------------
    # Determine latest available data
    # --------------------------------------------------

    latest_date = dates.max()

    latest_period = latest_date.to_period("M")

    # --------------------------------------------------
    # Determine freshness
    # --------------------------------------------------

    if latest_period >= investigation_period:
        freshness_status = "Fresh"
    else:
        freshness_status = "Stale"

    # --------------------------------------------------
    # Return freshness audit
    # --------------------------------------------------

    return {
        "source": source_name,
        "latest_data_date": latest_date.strftime(
            "%Y-%m-%d"
        ),
        "investigation_period": investigation_period.strftime(
            "%Y-%m"
        ),
        "freshness_status": freshness_status,
        "region": region
    }