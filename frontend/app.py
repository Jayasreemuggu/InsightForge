import sys
from pathlib import Path

# Allow imports from the project root
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import streamlit as st
import pandas as pd

from backend.analysis_pipeline import run_analysis


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="InsightForge",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("InsightForge")
st.subheader("Evidence-Driven KPI Investigation")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Investigation")

region = st.sidebar.selectbox(
    "Region",
    ["North", "South"]
)

date = st.sidebar.selectbox(
    "Period",
    ["2025-06-01", "2025-07-01"]
)

analyze_button = st.sidebar.button(
    "Analyze KPI"
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze_button:

    with st.spinner("Investigating KPI change..."):

        result = run_analysis(
            "data/sales.csv",
            "data/customer_feedback.csv",
            region,
            date
        )

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    if "error" in result:

        st.error(result["error"])

    else:

        st.success("Analysis completed")


        # ====================================================
        # KPI OVERVIEW
        # ====================================================

        st.header("KPI Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "KPI",
                result["kpi"]
            )

        with col2:
            st.metric(
                "Region",
                result["region"]
            )

        with col3:
            st.metric(
                "Revenue Change",
                f"{result['kpi_change']:.2f}%"
            )

        with col4:
            st.metric(
                "Evidence Strength",
                result["confidence"]
            )


        # ====================================================
        # REVENUE TREND
        # ====================================================

        st.divider()

        st.header("Revenue Trend")

        trend_df = pd.read_csv(
            "data/sales.csv"
        )

        trend_df["date"] = pd.to_datetime(
            trend_df["date"]
        )

        # Filter selected region
        region_trend = trend_df[
            trend_df["region"] == result["region"]
        ][
            ["date", "revenue"]
        ].sort_values("date")


        # ----------------------------------------------------
        # Month information
        # ----------------------------------------------------

        region_trend["month_number"] = (
            region_trend["date"].dt.month
        )

        region_trend["month"] = (
            region_trend["date"].dt.strftime("%b")
        )


        # ----------------------------------------------------
        # Force chronological month ordering
        # ----------------------------------------------------

        month_order = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec"
        ]

        region_trend["month"] = pd.Categorical(
            region_trend["month"],
            categories=month_order,
            ordered=True
        )

        region_trend = region_trend.sort_values(
            "month"
        )


        # ----------------------------------------------------
        # Revenue chart
        # ----------------------------------------------------

        chart_data = region_trend[
            [
                "month",
                "revenue"
            ]
        ].set_index(
            "month"
        )

        st.line_chart(
            chart_data["revenue"],
            use_container_width=True
        )


        # ----------------------------------------------------
        # Investigated month
        # ----------------------------------------------------

        investigated_date = pd.to_datetime(
            result["date"]
        )

        investigated_row = region_trend[
            region_trend["date"] == investigated_date
        ]

        if not investigated_row.empty:

            investigated_revenue = float(
                investigated_row.iloc[0]["revenue"]
            )

            investigated_month = (
                investigated_date.strftime("%B %Y")
            )

            st.metric(
                "Investigated Month Revenue",
                f"₹{investigated_revenue:,.0f}",
                f"{result['kpi_change']:+.2f}% vs previous month"
            )

            st.caption(
                f"Investigated period: "
                f"{investigated_month}"
            )


        # ====================================================
        # TOP OBSERVED DRIVERS
        # ====================================================

        st.divider()

        st.header(
            "Top Observed Drivers"
        )

        driver_df = pd.DataFrame(
            result["drivers"]
        )


        # ----------------------------------------------------
        # Clean driver names
        # ----------------------------------------------------

        driver_df["Driver"] = (
            driver_df["driver"]
            .astype(str)
            .str.replace(
                "_",
                " ",
                regex=False
            )
            .str.title()
        )


        # ----------------------------------------------------
        # Driver summary
        # ----------------------------------------------------

        for i, driver in enumerate(
            result["drivers"],
            start=1
        ):

            change = float(
                driver["percentage_change"]
            )

            if change > 0:
                direction = "increase"

            elif change < 0:
                direction = "decrease"

            else:
                direction = "no change"

            display_name = (
                driver["driver"]
                .replace("_", " ")
                .title()
            )

            st.write(
                f"**{i}. {display_name}** — "
                f"{change:+.2f}% "
                f"({direction})"
            )


        # ====================================================
        # DRIVER CHANGE COMPARISON
        # ====================================================

        st.subheader(
            "Driver Change Comparison"
        )

        driver_chart = driver_df[
            [
                "Driver",
                "percentage_change"
            ]
        ].copy()


        # Shorter labels for the chart
        driver_chart["Chart Label"] = (
            driver_chart["Driver"]
            .replace(
                {
                    "Product Usage":
                        "Product Usage",

                    "Support Resolution Hours":
                        "Support Resolution",

                    "Renewal Rate":
                        "Renewal Rate"
                }
            )
        )

        driver_chart = driver_chart[
            [
                "Chart Label",
                "percentage_change"
            ]
        ].set_index(
            "Chart Label"
        )


        st.bar_chart(
            driver_chart["percentage_change"],
            use_container_width=True
        )

        st.caption(
            "Positive values indicate an increase; "
            "negative values indicate a decrease."
        )


        # ====================================================
        # DRIVER DETAILS
        # ====================================================

        st.subheader(
            "Driver Details"
        )

        display_df = driver_df[
            [
                "Driver",
                "previous_value",
                "current_value",
                "percentage_change"
            ]
        ].copy()

        display_df.columns = [
            "Driver",
            "Previous Value",
            "Current Value",
            "Change (%)"
        ]

        display_df["Change (%)"] = (
            display_df["Change (%)"]
            .round(2)
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


        # ====================================================
        # SUPPORTING EVIDENCE
        # ====================================================

        st.divider()

        st.header(
            "Supporting Evidence"
        )

        st.caption(
            "Customer feedback is grouped according "
            "to the observed driver it supports."
        )


        # ----------------------------------------------------
        # Evidence for each driver
        # ----------------------------------------------------

        for driver in result["drivers"]:

            driver_name = (
                driver["driver"]
                .replace("_", " ")
                .title()
            )

            st.subheader(
                driver_name
            )

            supporting_evidence = driver.get(
                "supporting_evidence",
                []
            )

            if supporting_evidence:

                for evidence in supporting_evidence:

                    st.info(
                        evidence
                    )

            else:

                st.caption(
                    "No direct qualitative evidence "
                    "found for this driver."
                )


        # ====================================================
        # AI EXPLANATION
        # ====================================================

        st.divider()

        st.header(
            "AI Explanation"
        )

        st.markdown(
            result["explanation"]
        )


        # ====================================================
        # UNCERTAINTY
        # ====================================================

        st.subheader(
            "Uncertainty"
        )

        st.warning(
            result["uncertainty"]
        )


        # ====================================================
        # RECOMMENDED ACTION
        # ====================================================

        st.subheader(
            "Recommended Action"
        )

        st.success(
            result["recommended_action"]
        )


        # ====================================================
        # DISCLAIMER
        # ====================================================

        st.caption(
            "Evidence strength is a heuristic based on "
            "the available KPI change, driver count, and "
            "supporting evidence. It is not statistical "
            "confidence."
        )


# ============================================================
# INITIAL STATE
# ============================================================

else:

    st.info(
        "Select a region and period, then click "
        "**Analyze KPI** to investigate a business change."
    )