import pandas as pd

from backend.evidence.ranking import rank_evidence


def test_evidence_is_ranked_and_traceable():

    df = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-05-01",
            "2025-05-01",
            "2025-05-01"
        ]),
        "region": [
            "North",
            "North",
            "North"
        ],
        "customer_segment": [
            "Enterprise",
            "Enterprise",
            "Enterprise"
        ],
        "feedback": [
            "Support response was fast.",
            "Support issues were resolved quickly.",
            "Product performance was good."
        ]
    })

    result = rank_evidence(
        df,
        [
            "support_resolution_hours",
            "support response",
            "support"
        ]
    )

    assert not result.empty

    assert "evidence_score" in result.columns

    assert "evidence_strength" in result.columns

    assert "matched_keywords" in result.columns

    assert result.iloc[0]["evidence_score"] > 0

    assert len(
        result.iloc[0]["matched_keywords"]
    ) > 0


def test_unrelated_feedback_is_excluded():

    df = pd.DataFrame({
        "feedback": [
            "Support response was fast.",
            "The product interface looks modern."
        ]
    })

    result = rank_evidence(
        df,
        ["support response"]
    )

    assert len(result) == 1

    assert (
        "Support response was fast."
        == result.iloc[0]["feedback"]
    )


def test_empty_evidence_is_handled():

    df = pd.DataFrame(
        columns=["feedback"]
    )

    result = rank_evidence(
        df,
        ["support"]
    )

    assert result.empty

    assert "evidence_score" in result.columns

    assert "evidence_strength" in result.columns

    assert "matched_keywords" in result.columns