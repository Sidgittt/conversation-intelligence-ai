import pandas as pd
import plotly.express as px


def _valid_numeric_series(df, column):
    if column not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce").dropna()


def emotion_chart(df):
    if "Primary_Emotion" not in df.columns:
        return px.bar(title="Primary Emotions")
    data = df["Primary_Emotion"].astype(str).str.strip()
    data = data[~data.str.lower().isin(["", "nan", "none", "unknown"])]
    counts = data.value_counts().reset_index()
    counts.columns = ["Emotion", "Count"]
    return px.bar(counts, x="Emotion", y="Count", text="Count", title="Primary Emotions")


def conversation_type_chart(df):
    if "Conversation_Type" not in df.columns:
        return px.pie(title="Conversation Types")
    data = df["Conversation_Type"].astype(str).str.strip()
    data = data[~data.str.lower().isin(["", "nan", "none", "unknown"])]
    counts = data.value_counts().reset_index()
    counts.columns = ["Conversation Type", "Count"]
    return px.pie(counts, names="Conversation Type", values="Count", title="Conversation Types")


def sufficiency_chart(df):
    if "Conversation_Sufficiency" not in df.columns:
        return px.bar(title="Evidence Sufficiency")
    counts = df["Conversation_Sufficiency"].astype(str).str.title().value_counts().reset_index()
    counts.columns = ["Evidence Level", "Count"]
    return px.bar(counts, x="Evidence Level", y="Count", text="Count", title="Evidence Sufficiency")


def relationship_chart(df):
    mapping = {
        "Trust": "Trust_Score",
        "Communication": "Communication_Score",
        "Care": "Care_Score",
        "Respect": "Respect_Score",
        "Romance": "Romance_Score",
        "Friendship": "Friendship_Score",
    }
    rows = []
    for label, column in mapping.items():
        values = _valid_numeric_series(df, column)
        if not values.empty:
            rows.append({"Metric": label, "Score": round(values.mean(), 1)})
    if not rows:
        return px.bar(title="Relationship Scores — insufficient evidence")
    return px.bar(pd.DataFrame(rows), x="Metric", y="Score", text="Score", title="Average Relationship Scores")


def score_distribution_chart(df):
    columns = [
        "Communication_Score",
        "Quality_Engagement_Score",
        "Quality_Positivity_Score",
        "Quality_Emotional_Depth_Score",
        "Quality_Clarity_Score",
        "Conflict_Score",
        "Support_Score",
    ]
    rows = []
    labels = {
        "Communication_Score": "Communication",
        "Quality_Engagement_Score": "Engagement",
        "Quality_Positivity_Score": "Positivity",
        "Quality_Emotional_Depth_Score": "Emotional Depth",
        "Quality_Clarity_Score": "Clarity",
        "Conflict_Score": "Conflict",
        "Support_Score": "Support",
    }
    for column in columns:
        values = _valid_numeric_series(df, column)
        for value in values:
            rows.append({"Metric": labels[column], "Score": value})
    if not rows:
        return px.box(title="Score Distribution — insufficient evidence")
    return px.box(pd.DataFrame(rows), x="Metric", y="Score", points="all", title="Score Distribution")


def toxicity_chart(df):
    if "Toxicity_Level" not in df.columns:
        return px.bar(title="Toxicity Distribution")
    data = df["Toxicity_Level"].astype(str).str.title()
    counts = data.value_counts().reset_index()
    counts.columns = ["Toxicity Level", "Count"]
    return px.bar(counts, x="Toxicity Level", y="Count", text="Count", title="Toxicity Distribution")
