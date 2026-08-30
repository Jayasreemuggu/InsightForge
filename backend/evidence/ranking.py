import pandas as pd


def rank_evidence(
    df: pd.DataFrame,
    keywords: list[str]
) -> pd.DataFrame:

    df = df.copy()

    if df.empty:
        df["evidence_score"] = pd.Series(dtype=float)
        return df

    def score(text):

        text = str(text).lower()
        score_value = 0

        for keyword in keywords:

            keyword = str(keyword).lower().replace("_", " ")

            # Exact phrase match
            if keyword in text:
                score_value += 3
                continue

            # Individual keyword match
            for word in keyword.split():

                if len(word) >= 4 and word in text:
                    score_value += 1

        return score_value

    df["evidence_score"] = (
        df["feedback"]
        .apply(score)
    )

    return (
        df[
            df["evidence_score"] > 0
        ]
        .sort_values(
            "evidence_score",
            ascending=False
        )
        .reset_index(drop=True)
    )