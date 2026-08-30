import pandas as pd
from backend.freshness import check_source_freshness


SOURCE_CONTRACTS = {
    "sales": {
        "source": "Sales / KPI data",
        "grain": "Transaction / record level",
        "analysis_grain": "Monthly + Region",
        "refresh_cadence": "Source-defined",
    },

    "drivers": {
        "source": "Driver metrics",
        "grain": "Monthly + Region",
        "analysis_grain": "Monthly + Region",
        "refresh_cadence": "Source-defined",
    },

    "customer_feedback": {
        "source": "Customer feedback",
        "grain": "Individual feedback event",
        "analysis_grain": "Monthly + Region",
        "refresh_cadence": "Event-driven",
    },
}


def reconcile_sources(
    sales_df: pd.DataFrame,
    feedback_df: pd.DataFrame,
    region: str,
    date: str
):
    """
    Reconcile heterogeneous sources before investigation.

    The sources may have different grains:
    - sales records
    - monthly driver metrics
    - individual customer feedback events

    All sources are aligned to the investigation key:

        Region + Month

    Returns a reconciliation audit describing:
    - source grain
    - analysis grain
    - refresh characteristics
    - records available
    - alignment status
    """

    investigation_date = pd.to_datetime(date)

    # --------------------------------------------------
    # Validate required columns
    # --------------------------------------------------

    required_sales_columns = {
        "region",
        "date"
    }

    required_feedback_columns = {
        "region",
        "date",
        "feedback"
    }

    missing_sales = (
        required_sales_columns
        - set(sales_df.columns)
    )

    missing_feedback = (
        required_feedback_columns
        - set(feedback_df.columns)
    )

    if missing_sales:
        raise ValueError(
            f"Sales source missing required columns: "
            f"{sorted(missing_sales)}"
        )

    if missing_feedback:
        raise ValueError(
            f"Feedback source missing required columns: "
            f"{sorted(missing_feedback)}"
        )

    # --------------------------------------------------
    # Normalize dates
    # --------------------------------------------------

    sales = sales_df.copy()
    feedback = feedback_df.copy()

    sales["date"] = pd.to_datetime(
        sales["date"],
        errors="coerce"
    )

    feedback["date"] = pd.to_datetime(
        feedback["date"],
        errors="coerce"
    )

    # --------------------------------------------------
    # Align everything to investigation month
    # --------------------------------------------------

    investigation_period = investigation_date.to_period("M")

    sales["analysis_month"] = (
        sales["date"].dt.to_period("M")
    )

    feedback["analysis_month"] = (
        feedback["date"].dt.to_period("M")
    )

    sales_aligned = sales[
        (sales["region"] == region) &
        (sales["analysis_month"] == investigation_period)
    ]

    feedback_aligned = feedback[
        (feedback["region"] == region) &
        (feedback["analysis_month"] == investigation_period)
    ]
    
    # --------------------------------------------------
    # Source freshness
    # --------------------------------------------------

    source_freshness = [
        check_source_freshness(
            source_name="sales",
            df=sales,
            investigation_date=date
        ),
        check_source_freshness(
            source_name="customer_feedback",
            df=feedback,
            investigation_date=date
        )
    ]

    # --------------------------------------------------
    # Build reconciliation audit
    # --------------------------------------------------

    audit = {
        "investigation_key": {
            "region": region,
            "period": investigation_date.strftime("%Y-%m"),
            "alignment_grain": "Monthly + Region"
        },

        "sources": []
    }

    # Sales source
    audit["sources"].append({
        "source": SOURCE_CONTRACTS["sales"]["source"],
        "source_grain": SOURCE_CONTRACTS["sales"]["grain"],
        "analysis_grain": SOURCE_CONTRACTS["sales"]["analysis_grain"],
        "refresh_cadence": SOURCE_CONTRACTS["sales"]["refresh_cadence"],
        "records_aligned": int(len(sales_aligned)),
        "aligned": bool(len(sales_aligned) > 0),
        "alignment_method": (
            "Region filter + calendar-month normalization"
        )
    })

    # Driver source
    audit["sources"].append({
        "source": SOURCE_CONTRACTS["drivers"]["source"],
        "source_grain": SOURCE_CONTRACTS["drivers"]["grain"],
        "analysis_grain": SOURCE_CONTRACTS["drivers"]["analysis_grain"],
        "refresh_cadence": SOURCE_CONTRACTS["drivers"]["refresh_cadence"],
        "records_aligned": "Derived from sales analysis",
        "aligned": True,
        "alignment_method": (
            "Monthly + Region driver analysis"
        )
    })

    # Customer feedback source
    audit["sources"].append({
        "source": SOURCE_CONTRACTS["customer_feedback"]["source"],
        "source_grain": SOURCE_CONTRACTS["customer_feedback"]["grain"],
        "analysis_grain": SOURCE_CONTRACTS["customer_feedback"]["analysis_grain"],
        "refresh_cadence": SOURCE_CONTRACTS["customer_feedback"]["refresh_cadence"],
        "records_aligned": int(len(feedback_aligned)),
        "aligned": True,
        "alignment_method": (
            "Region filter + calendar-month normalization"
        )
    })

    # --------------------------------------------------
    # Overall reconciliation status
    # --------------------------------------------------

    audit["reconciliation_status"] = "reconciled"

    audit["reconciliation_rule"] = (
        "Heterogeneous sources are aligned to the common "
        "investigation key: Region + Calendar Month. "
        "Source-specific grains are preserved before "
        "cross-source comparison."
    )
    
    audit["source_freshness"] = source_freshness
    return audit