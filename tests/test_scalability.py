import time
import pandas as pd

from backend.analysis_pipeline import run_analysis


def test_scalability_large_dataset(tmp_path):

    # Create a larger synthetic sales dataset
    rows = []

    regions = ["North", "South", "East", "West"]

    for month in pd.date_range("2024-01-01", "2025-06-01", freq="MS"):

        for region in regions:

            for i in range(250):

                rows.append({
                    "date": month,
                    "region": region,
                    "revenue": 1000 + (i % 100)
                })

    sales_df = pd.DataFrame(rows)

    sales_file = tmp_path / "large_sales.csv"
    sales_df.to_csv(sales_file, index=False)

    # Minimal feedback dataset
    feedback_df = pd.DataFrame({
        "date": ["2025-06-01"],
        "region": ["North"],
        "feedback": [
            "Product usage has decreased because several issues remain unresolved."
        ]
    })

    feedback_file = tmp_path / "feedback.csv"
    feedback_df.to_csv(feedback_file, index=False)

    start = time.perf_counter()

    result = run_analysis(
        sales_file=str(sales_file),
        feedback_file=str(feedback_file),
        region="North",
        date="2025-06-01",
        persona="Executive"
    )

    elapsed = time.perf_counter() - start

    print(f"\nScalability test runtime: {elapsed:.3f}s")
    print(f"Rows processed: {len(sales_df)}")

    # Pipeline must return a valid structured result
    assert isinstance(result, dict)

    # Pipeline should finish within a reasonable test limit
    assert elapsed < 30

    print("SCALABILITY TEST PASSED")