import pandas as pd


def reconcile_sources(
    sales_file: str,
    product_usage_file: str,
    renewal_file: str,
    support_file: str
) -> pd.DataFrame:

    # ============================================================
    # 1. SALES SOURCE
    # Grain: monthly + region
    # ============================================================

    sales = pd.read_csv(sales_file)

    sales["date"] = pd.to_datetime(sales["date"])

    sales["month"] = (
        sales["date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    sales_monthly = (
        sales
        .groupby(
            ["month", "region"],
            as_index=False
        )
        .agg(
            revenue=("revenue", "sum"),
            orders=("orders", "sum")
        )
    )


    # ============================================================
    # 2. PRODUCT USAGE SOURCE
    # Grain: daily + region
    # Reconcile → monthly + region
    # ============================================================

    product = pd.read_csv(product_usage_file)

    product["date"] = pd.to_datetime(product["date"])

    product["month"] = (
        product["date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    product_monthly = (
        product
        .groupby(
            ["month", "region"],
            as_index=False
        )
        .agg(
            product_usage=(
                "product_usage",
                "mean"
            )
        )
    )


    # ============================================================
    # 3. RENEWAL SOURCE
    # Grain: customer + week
    # Reconcile → monthly + region
    # ============================================================

    renewal = pd.read_csv(renewal_file)

    renewal["date"] = pd.to_datetime(
        renewal["date"]
    )

    renewal["month"] = (
        renewal["date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    renewal_monthly = (
        renewal
        .groupby(
            ["month", "region"],
            as_index=False
        )
        .agg(
            renewal_rate=(
                "renewal_rate",
                "mean"
            )
        )
    )


    # ============================================================
    # 4. SUPPORT SOURCE
    # Grain: individual ticket + day
    # Reconcile → monthly + region
    # ============================================================

    support = pd.read_csv(support_file)

    support["date"] = pd.to_datetime(
        support["date"]
    )

    support["month"] = (
        support["date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    support_monthly = (
        support
        .groupby(
            ["month", "region"],
            as_index=False
        )
        .agg(
            support_resolution_hours=(
                "support_resolution_hours",
                "mean"
            )
        )
    )


    # ============================================================
    # 5. RECONCILE ALL SOURCES
    # Common analytical grain:
    #
    #       month + region
    # ============================================================

    result = sales_monthly.merge(
        product_monthly,
        on=["month", "region"],
        how="left"
    )

    result = result.merge(
        renewal_monthly,
        on=["month", "region"],
        how="left"
    )

    result = result.merge(
        support_monthly,
        on=["month", "region"],
        how="left"
    )


    # ============================================================
    # 6. Standardize final schema
    # ============================================================

    result = result.rename(
        columns={
            "month": "date"
        }
    )

    result = result.sort_values(
        ["region", "date"]
    ).reset_index(drop=True)


    return result