import pandas as pd

from backend.freshness import check_source_freshness


SOURCE_CONTRACTS = {
    "sales": {
        "source": "Sales / KPI data",
        "grain": "Transaction / record level",
        "analysis_grain": "Monthly + Region",
        "refresh_cadence": "Source-defined",
        "required_columns": ["date", "region", "revenue"],
    },
    "product_usage": {
        "source": "Product usage data",
        "grain": "Monthly + Region",
        "analysis_grain": "Monthly + Region",
        "refresh_cadence": "Source-defined",
        "required_columns": ["date", "region", "product_usage"],
    },
    "renewal_data": {
        "source": "Renewal data",
        "grain": "Monthly + Region",
        "analysis_grain": "Monthly + Region",
        "refresh_cadence": "Source-defined",
        "required_columns": ["date", "region", "renewal_rate"],
    },
    "support_tickets": {
        "source": "Support ticket data",
        "grain": "Monthly + Region",
        "analysis_grain": "Monthly + Region",
        "refresh_cadence": "Source-defined",
        "required_columns": [
            "date",
            "region",
            "support_resolution_hours",
        ],
    },
    "customer_feedback": {
        "source": "Customer feedback",
        "grain": "Individual feedback event",
        "analysis_grain": "Monthly + Region",
        "refresh_cadence": "Event-driven",
        "required_columns": [
            "date",
            "region",
            "feedback",
        ],
    },
}


def _validate_source(name, df):
    """Validate the schema of one source."""

    if df is None:
        raise ValueError(f"{name} source is None.")

    required = set(
        SOURCE_CONTRACTS[name]["required_columns"]
    )

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{name} source missing required columns: "
            f"{sorted(missing)}"
        )


def _normalize_dates(df):
    """Return a copy with normalized datetime values."""

    result = df.copy()

    result["date"] = pd.to_datetime(
        result["date"],
        errors="coerce"
    )

    result = result.dropna(
        subset=["date"]
    )

    result["analysis_month"] = (
        result["date"].dt.to_period("M")
    )

    return result


def _align_source(
    df,
    region,
    investigation_period
):
    """Align a source to Region + Calendar Month."""

    return df[
        (df["region"] == region)
        &
        (df["analysis_month"] == investigation_period)
    ].copy()


def reconcile_sources(
    sales_df: pd.DataFrame,
    feedback_df: pd.DataFrame,
    region: str,
    date: str,
    product_usage_df: pd.DataFrame = None,
    renewal_df: pd.DataFrame = None,
    support_tickets_df: pd.DataFrame = None,
):
    """
    Reconcile all heterogeneous InsightForge sources.

    Common investigation key:

        Region + Calendar Month

    Quantitative sources:
        sales
        product_usage
        renewal_data
        support_tickets

    Qualitative source:
        customer_feedback

    Source-specific grains are preserved before
    cross-source comparison.
    """

    investigation_date = pd.to_datetime(date)

    investigation_period = (
        investigation_date.to_period("M")
    )

    # --------------------------------------------------
    # Validate sources
    # --------------------------------------------------

    _validate_source(
        "sales",
        sales_df
    )

    _validate_source(
        "customer_feedback",
        feedback_df
    )

    # Optional sources are required for complete
    # heterogeneous reconciliation.
    if product_usage_df is None:
        raise ValueError(
            "product_usage source is required."
        )

    if renewal_df is None:
        raise ValueError(
            "renewal_data source is required."
        )

    if support_tickets_df is None:
        raise ValueError(
            "support_tickets source is required."
        )

    _validate_source(
        "product_usage",
        product_usage_df
    )

    _validate_source(
        "renewal_data",
        renewal_df
    )

    _validate_source(
        "support_tickets",
        support_tickets_df
    )

    # --------------------------------------------------
    # Normalize dates
    # --------------------------------------------------

    sources = {
        "sales": _normalize_dates(sales_df),
        "product_usage": _normalize_dates(
            product_usage_df
        ),
        "renewal_data": _normalize_dates(
            renewal_df
        ),
        "support_tickets": _normalize_dates(
            support_tickets_df
        ),
        "customer_feedback": _normalize_dates(
            feedback_df
        ),
    }

    # --------------------------------------------------
    # Align sources
    # --------------------------------------------------

    aligned = {}

    for name, source_df in sources.items():
        aligned[name] = _align_source(
            source_df,
            region,
            investigation_period
        )

    # --------------------------------------------------
    # Freshness
    # --------------------------------------------------

    source_freshness = []

    for name, source_df in sources.items():

        source_freshness.append(
            check_source_freshness(
                source_name=name,
                df=source_df,
                investigation_date=date,
                region=region
            )
        )

    # --------------------------------------------------
    # Build source audit
    # --------------------------------------------------

    audit = {
        "investigation_key": {
            "region": region,
            "period": investigation_period.strftime(
                "%Y-%m"
            ),
            "alignment_grain": "Monthly + Region",
        },
        "sources": [],
    }

    for name, source_df in sources.items():

        contract = SOURCE_CONTRACTS[name]

        aligned_df = aligned[name]

        audit["sources"].append({
            "source": contract["source"],
            "source_id": name,
            "source_grain": contract["grain"],
            "analysis_grain": contract[
                "analysis_grain"
            ],
            "refresh_cadence": contract[
                "refresh_cadence"
            ],
            "records_available": int(
                len(source_df)
            ),
            "records_aligned": int(
                len(aligned_df)
            ),
            "aligned": bool(
                len(aligned_df) > 0
            ),
            "coverage": (
                "Available"
                if len(aligned_df) > 0
                else "Missing for investigation period"
            ),
            "alignment_method": (
                "Region filter + "
                "calendar-month normalization"
            ),
        })

    # --------------------------------------------------
    # Overall reconciliation
    # --------------------------------------------------

    all_sources_aligned = all(
        source["aligned"]
        for source in audit["sources"]
    )

    audit["reconciliation_status"] = (
        "reconciled"
        if all_sources_aligned
        else "partially_reconciled"
    )

    audit["reconciliation_rule"] = (
        "All heterogeneous sources are aligned "
        "using the common investigation key "
        "Region + Calendar Month. Source-specific "
        "grains are preserved before comparison."
    )

    audit["source_freshness"] = source_freshness

    # --------------------------------------------------
    # Cross-source driver coverage
    # --------------------------------------------------

    audit["driver_sources"] = {
        "product_usage": {
            "source": "product_usage",
            "available": bool(
                len(aligned["product_usage"]) > 0
            ),
        },
        "renewal_rate": {
            "source": "renewal_data",
            "available": bool(
                len(aligned["renewal_data"]) > 0
            ),
        },
        "support_resolution_hours": {
            "source": "support_tickets",
            "available": bool(
                len(aligned["support_tickets"]) > 0
            ),
        },
    }

    return audit