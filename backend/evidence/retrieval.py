import pandas as pd


def retrieve_feedback(
    file_path: str,
    region: str,
    date: str,
    keywords: list[str]
) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    df["date"] = pd.to_datetime(df["date"])

    filtered = df[
        (df["region"] == region) &
        (df["date"] == pd.to_datetime(date))
    ].copy()

    if filtered.empty:
        return filtered

    if not keywords:
        return filtered

    # Convert driver names such as
    # "support_resolution_hours" into meaningful terms.
    terms = []

    for keyword in keywords:
        keyword = str(keyword).lower().replace("_", " ")

        terms.append(keyword)

        for word in keyword.split():
            if len(word) >= 4:
                terms.append(word)

    # Remove duplicates while preserving order
    terms = list(dict.fromkeys(terms))

    def matches_feedback(text):
        text = str(text).lower()

        return any(
            term in text
            for term in terms
        )

    relevant = filtered[
        filtered["feedback"].apply(matches_feedback)
    ].copy()

    return relevant