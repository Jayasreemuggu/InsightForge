import pandas as pd

from backend.freshness import check_source_freshness


def test_fresh_source():

    df = pd.DataFrame({
        "date": [
            "2025-05-01",
            "2025-06-01",
            "2025-06-15"
        ],
        "region": [
            "North",
            "North",
            "North"
        ]
    })

    result = check_source_freshness(
        source_name="sales",
        df=df,
        investigation_date="2025-06-01"
    )

    assert result["freshness_status"] == "Fresh"
    assert result["latest_data_date"] == "2025-06-15"

    print("\nFreshness test:")
    print(result)


def test_stale_source():

    df = pd.DataFrame({
        "date": [
            "2025-03-01",
            "2025-04-01"
        ],
        "region": [
            "North",
            "North"
        ]
    })

    result = check_source_freshness(
        source_name="sales",
        df=df,
        investigation_date="2025-06-01"
    )

    assert result["freshness_status"] == "Stale"

    print("\nStale-source test:")
    print(result)


def test_unavailable_source():

    df = pd.DataFrame({
        "region": ["North"]
    })

    result = check_source_freshness(
        source_name="sales",
        df=df,
        investigation_date="2025-06-01"
    )

    assert result["freshness_status"] == "Unavailable"

    print("\nUnavailable-source test:")
    print(result)


if __name__ == "__main__":

    test_fresh_source()
    test_stale_source()
    test_unavailable_source()

    print("\nTEST PASSED")