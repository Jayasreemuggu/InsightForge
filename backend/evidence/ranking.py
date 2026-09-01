import pandas as pd


def rank_evidence(
    df: pd.DataFrame,
    keywords: list[str]
) -> pd.DataFrame:

    df = df.copy()

    # --------------------------------------------------
    # Empty evidence
    # --------------------------------------------------

    if df.empty:

        df["evidence_score"] = pd.Series(
            dtype=float
        )

        df["evidence_strength"] = pd.Series(
            dtype=str
        )

        df["matched_keywords"] = pd.Series(
            dtype=object
        )

        return df

    # --------------------------------------------------
    # Calculate score and matched keywords
    # --------------------------------------------------

    def analyze_text(text):

        text = str(text).lower()

        score_value = 0
        matched = []

        for keyword in keywords:

            original_keyword = str(keyword)

            normalized_keyword = (
                original_keyword
                .lower()
                .replace("_", " ")
            )

            # Exact phrase match
            if normalized_keyword in text:

                score_value += 3

                matched.append(
                    original_keyword
                )

                continue

            # Individual keyword match
            keyword_matched = False

            for word in normalized_keyword.split():

                if len(word) >= 4 and word in text:

                    score_value += 1
                    keyword_matched = True

            if keyword_matched:

                matched.append(
                    original_keyword
                )

        # Remove duplicate matches while
        # preserving keyword order.
        matched = list(
            dict.fromkeys(matched)
        )

        return score_value, matched

    analyzed = (
        df["feedback"]
        .apply(analyze_text)
    )

    df["evidence_score"] = analyzed.apply(
        lambda x: x[0]
    )

    df["matched_keywords"] = analyzed.apply(
        lambda x: x[1]
    )

    # --------------------------------------------------
    # Evidence strength
    # --------------------------------------------------

    def classify_strength(score_value):

        if score_value >= 6:
            return "Strong"

        if score_value >= 3:
            return "Moderate"

        return "Weak"

    df["evidence_strength"] = (
        df["evidence_score"]
        .apply(classify_strength)
    )

    # --------------------------------------------------
    # Keep only relevant evidence
    # --------------------------------------------------

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