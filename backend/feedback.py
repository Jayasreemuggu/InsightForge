from pathlib import Path
from datetime import datetime
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = PROJECT_ROOT / "data" / "insight_feedback.csv"


COLUMNS = [
    "timestamp",
    "region",
    "date",
    "kpi",
    "persona",
    "feedback_type",
    "rating",
    "correction",
    "comment",
]


def ensure_feedback_file():
    FEEDBACK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not FEEDBACK_FILE.exists():
        pd.DataFrame(
            columns=COLUMNS
        ).to_csv(
            FEEDBACK_FILE,
            index=False
        )


def record_feedback(
    region: str,
    date: str,
    kpi: str,
    persona: str,
    feedback_type: str,
    rating: int | None = None,
    correction: str = "",
    comment: str = "",
):
    """
    Store analyst/business-user feedback
    for a generated insight.
    """

    ensure_feedback_file()

    if rating is not None:
        rating = int(rating)

        if rating < 1 or rating > 5:
            raise ValueError(
                "rating must be between 1 and 5"
            )

    valid_feedback_types = {
        "useful",
        "not_useful",
        "correct",
        "incorrect",
        "correction",
    }

    if feedback_type not in valid_feedback_types:
        raise ValueError(
            f"Invalid feedback_type: {feedback_type}"
        )

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "region": region,
        "date": date,
        "kpi": kpi,
        "persona": persona,
        "feedback_type": feedback_type,
        "rating": rating,
        "correction": correction,
        "comment": comment,
    }

    df = pd.DataFrame([record])

    df.to_csv(
        FEEDBACK_FILE,
        mode="a",
        header=False,
        index=False
    )

    return record


def get_feedback_summary():
    """
    Return aggregate feedback statistics.
    """

    ensure_feedback_file()

    df = pd.read_csv(
        FEEDBACK_FILE
    )

    if df.empty:
        return {
            "total_feedback": 0,
            "average_rating": None,
            "useful_feedback": 0,
            "not_useful_feedback": 0,
            "corrections": 0,
        }

    ratings = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )

    return {
        "total_feedback": int(len(df)),
        "average_rating": (
            round(float(ratings.mean()), 2)
            if ratings.notna().any()
            else None
        ),
        "useful_feedback": int(
            (df["feedback_type"] == "useful").sum()
        ),
        "not_useful_feedback": int(
            (df["feedback_type"] == "not_useful").sum()
        ),
        "corrections": int(
            (df["feedback_type"] == "correction").sum()
        ),
    }

def get_relevant_feedback(
    region: str,
    date: str,
    kpi: str,
    persona: str,
):
    """
    Retrieve previous analyst/business feedback
    relevant to the current investigation.
    """

    ensure_feedback_file()

    df = pd.read_csv(FEEDBACK_FILE)

    if df.empty:
        return []

    # Normalize values for matching
    df["region"] = df["region"].astype(str).str.strip().str.lower()
    df["date"] = df["date"].astype(str).str.strip()
    df["kpi"] = df["kpi"].astype(str).str.strip().str.lower()
    df["persona"] = df["persona"].astype(str).str.strip().str.lower()

    matches = df[
        (df["region"] == str(region).strip().lower()) &
        (df["date"] == str(date).strip()) &
        (df["kpi"] == str(kpi).strip().lower()) &
        (df["persona"] == str(persona).strip().lower())
    ]

    if matches.empty:
        return []

    results = []

    for _, row in matches.iterrows():
        results.append({
            "timestamp": row["timestamp"],
            "feedback_type": row["feedback_type"],
            "rating": (
                int(row["rating"])
                if pd.notna(row["rating"])
                else None
            ),
            "correction": (
                str(row["correction"])
                if pd.notna(row["correction"])
                else ""
            ),
            "comment": (
                str(row["comment"])
                if pd.notna(row["comment"])
                else ""
            ),
        })

    return results