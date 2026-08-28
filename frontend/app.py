import sys
from pathlib import Path

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

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

st.subheader(
    "Evidence-Driven KPI Investigation"
)

st.caption(
    "Detect significant KPI changes, identify observed drivers, "
    "connect customer evidence, and generate an evidence-grounded AI insight."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Investigation")

sales_df = pd.read_csv("data/sales.csv")

sales_df["date"] = pd.to_datetime(
    sales_df["date"]
)

available_regions = (
    sales_df["region"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

region = st.sidebar.selectbox(
    "Region",
    available_regions
)

available_dates = (
    sales_df["date"]
    .drop_duplicates()
    .sort_values()
    .dt.strftime("%Y-%m-%d")
    .tolist()
)

date = st.sidebar.selectbox(
    "Period",
    available_dates,
    format_func=lambda x:
        pd.to_datetime(x).strftime("%B %Y")
)

analyze_button = st.sidebar.button(
    "Analyze KPI",
    width="stretch"
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
                f"{result['kpi_change']:+.2f}%"
            )

        with col4:
            st.metric(
                "Evidence Strength",
                result["confidence"]
            )


        # ====================================================
        # INVESTIGATION SUMMARY
        # ====================================================

        st.divider()

        st.header("Investigation Summary")

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:

            st.markdown(
                f"""
                **Investigated Period**

                {pd.to_datetime(result["date"]).strftime("%B %Y")}
                """
            )

        with summary_col2:

            change = float(result["kpi_change"])

            if change > 0:
                movement = "Revenue increased"
            elif change < 0:
                movement = "Revenue decreased"
            else:
                movement = "Revenue remained unchanged"

            st.markdown(
                f"""
                **KPI Movement**

                {movement} by **{abs(change):.2f}%**
                """
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

        region_trend = (
            trend_df[
                trend_df["region"] == result["region"]
            ][
                ["date", "revenue"]
            ]
            .sort_values("date")
            .copy()
        )

        region_trend["month_number"] = (
            region_trend["date"].dt.month
        )

        region_trend["month"] = (
            region_trend["date"].dt.strftime("%b")
        )

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
            "month_number"
        )

        chart_data = (
            region_trend[
                ["month", "revenue"]
            ]
            .set_index("month")
        )

        st.line_chart(
            chart_data["revenue"],
            width="stretch"
        )

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

            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:

                st.metric(
                    "Investigated Month Revenue",
                    f"₹{investigated_revenue:,.0f}"
                )

            with metric_col2:

                st.metric(
                    "Change vs Previous Month",
                    f"{result['kpi_change']:+.2f}%"
                )

            st.caption(
                f"Investigated period: {investigated_month}"
            )


        # ====================================================
        # TOP OBSERVED DRIVERS
        # ====================================================

        st.divider()

        st.header("Top Observed Drivers")

        driver_df = pd.DataFrame(
            result["drivers"]
        )

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


        # ====================================================
        # DRIVER CARDS
        # ====================================================

        driver_columns = st.columns(
            len(driver_df)
        )

        for i, (_, driver) in enumerate(
            driver_df.iterrows()
        ):

            change = float(
                driver["percentage_change"]
            )

            display_name = driver["Driver"]

            if change > 0:
                direction = "↑ Increase"
            elif change < 0:
                direction = "↓ Decrease"
            else:
                direction = "→ No Change"

            with driver_columns[i]:
                
                st.write(
                    f"**{display_name}**"
                )

                st.markdown(
                    f"### {change:+.2f}%"
                )

                st.caption(
                    direction
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
        driver_chart["Driver"] = driver_chart["Driver"].replace({
            "Support Resolution Hours": "Support Resolution",
            "Product Usage": "Product Usage",
            "Renewal Rate": "Renewal Rate"
        })

        driver_chart = driver_chart.sort_values(
            "percentage_change"
        )

        driver_chart = driver_chart.set_index(
            "Driver"
        )

        st.bar_chart(
            driver_chart["percentage_change"],
            horizontal=True,
            width="stretch",
            height=280
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

        display_rows = []

        for driver in result["drivers"]:

            driver_name = (
                driver["driver"]
                .replace("_", " ")
                .title()
            )

            display_rows.append(
                {
                    "Driver": driver_name,

                    "Previous Value": driver.get(
                        "previous_value",
                        "-"
                    ),

                    "Current Value": driver.get(
                        "current_value",
                        "-"
                    ),

                    "Change (%)": round(
                        float(
                            driver.get(
                                "percentage_change",
                                0
                            )
                        ),
                        2
                    ),

                    "Correlation": round(
                        float(
                            driver.get(
                                "correlation",
                                0
                            )
                        ),
                        3
                    ),

                    "Historical Observations": driver.get(
                        "historical_observations",
                        0
                    ),
                    
                    "Correlation Reliability": driver.get(
                        "correlation_reliability",
                        "Unknown"
                    ),
                    
                    "Correlation p-value": round(
                        float(
                            driver.get(
                                "correlation_p_value",
                                1.0
                            )
                        ),
                        4
                    ),

                    "Correlation Significance": driver.get(
                        "correlation_significance",
                        "Unknown"
                    ),
                    
                    "Driver Score": round(
                        float(
                            driver.get(
                                "driver_score",
                                0
                            )
                        ),
                        2
                    )
                }
            )

        display_df = pd.DataFrame(
            display_rows
        )

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )

        st.caption(
            "Correlation and driver score represent observed "
            "historical associations. They do not establish causation."
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
            "confidence. Observed associations do not "
            "establish causation."
        )


# ============================================================
# INITIAL STATE
# ============================================================

else:

    st.info(
        "Select a region and period, then click "
        "**Analyze KPI** to investigate a business change."
    )

    st.markdown(
        """
        ### Investigation Workflow

        **1. Detect** → Identify significant revenue movement

        **2. Analyze** → Find the strongest observed drivers

        **3. Retrieve** → Find relevant customer feedback

        **4. Rank** → Prioritize supporting evidence

        **5. Explain** → Generate an evidence-grounded AI explanation

        **6. Recommend** → Produce one practical next action
        """
    )