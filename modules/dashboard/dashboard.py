import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WhatsApp AI",
    page_icon="💬",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

st.title("💬 WhatsApp AI")
st.caption("Context-Aware Conversation Intelligence")

csv = Path("output") / "ai_analysis.csv"

if not csv.exists():
    st.error("ai_analysis.csv not found.")
    st.stop()

df = pd.read_csv(csv)

if df.empty:
    st.warning("No analyzed conversations are available.")
    st.stop()


# ============================================================
# HELPERS
# ============================================================

def numeric_value(value):
    return pd.to_numeric(value, errors="coerce")


def safe_mean(dataframe, column):
    if column not in dataframe.columns:
        return None

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce"
    ).dropna()

    if values.empty:
        return None

    return round(values.mean(), 1)


def clean_context(value):
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()

    replacements = {
        "romantic": "Romantic",
        "romance": "Romantic",
        "friendship": "Friendship",
        "professional": "Professional",
        "career": "Career",
        "personal_growth": "Personal Growth",
        "personal growth": "Personal Growth",
        "family": "Family",
        "casual": "Casual",
        "emotional_support": "Emotional Support",
        "emotional support": "Emotional Support",
        "financial": "Financial",
        "future_planning": "Future Planning",
        "future planning": "Future Planning",
        "marriage": "Marriage",
        "conflict": "Conflict",
        "reconciliation": "Reconciliation",
        "travel": "Travel",
        "education": "Education",
        "health": "Health",
        "humor": "Humor",
        "daily_life": "Daily Life",
        "daily life": "Daily Life",
        "self_growth": "Personal Growth"
    }

    return replacements.get(
        value,
        value.replace("_", " ").title()
    )


def get_context_columns(dataframe):
    """
    Return all available AI-generated context columns.
    """

    if "Primary_Context" not in dataframe.columns:
        return []

    contexts = []

    for value in dataframe["Primary_Context"].dropna():

        context = clean_context(value)

        if context and context not in contexts:
            contexts.append(context)

    return sorted(contexts)


def get_secondary_contexts(row):
    """
    Extract AI-generated secondary contexts.
    """

    if "Secondary_Contexts" not in row.index:
        return []

    value = row["Secondary_Contexts"]

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    # Handle common stored formats
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = text.replace('"', "")
    text = text.replace("'", "")

    contexts = []

    for item in text.split(","):

        item = item.strip()

        if item:
            contexts.append(
                clean_context(item)
            )

    return contexts


def get_context_score(row, context):
    """
    Determine whether a particular AI-generated context
    is represented in a conversation.

    Primary context = strong evidence.
    Secondary context = additional evidence.
    """

    primary = ""

    if "Primary_Context" in row.index:
        primary = clean_context(
            row["Primary_Context"]
        )

    if primary == context:
        return 100

    secondary = get_secondary_contexts(row)

    if context in secondary:
        return 50

    return 0


# ============================================================
# NORMALIZE AI CONTEXT
# ============================================================

if "Primary_Context" not in df.columns:

    st.error(
        "Primary_Context is not available in ai_analysis.csv."
    )

    st.info(
        "The dashboard requires the AI-generated context fields."
    )

    st.stop()


df["Display_Context"] = df["Primary_Context"].apply(
    clean_context
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Conversation Context")

available_contexts = get_context_columns(df)

context_options = [
    "All Contexts"
] + available_contexts

selected_context = st.sidebar.selectbox(
    "View",
    context_options
)


# ============================================================
# FILTER
# ============================================================

if selected_context == "All Contexts":

    filtered_df = df.copy()

else:

    primary_match = (
        df["Display_Context"] == selected_context
    )

    secondary_match = df.apply(
        lambda row: selected_context
        in get_secondary_contexts(row),
        axis=1
    )

    filtered_df = df[
        primary_match | secondary_match
    ].copy()


if filtered_df.empty:

    st.warning(
        "No analyzed conversations were found for this context."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

if selected_context == "All Contexts":

    st.subheader(
        "Conversation Intelligence Overview"
    )

else:

    st.subheader(
        f"{selected_context} Intelligence"
    )

st.caption(
    f"{len(filtered_df)} analyzed conversation"
    + (
        "s"
        if len(filtered_df) != 1
        else ""
    )
)


# ============================================================
# KPI DEFINITIONS
# ============================================================

universal_metrics = [
    (
        "Communication",
        "Communication_Score"
    ),
    (
        "Engagement",
        "Engagement_Score"
    ),
    (
        "Positivity",
        "Positivity_Score"
    ),
    (
        "Emotional Depth",
        "Emotional_Depth_Score"
    ),
    (
        "Clarity",
        "Clarity_Score"
    ),
    (
        "Conflict",
        "Conflict_Score"
    ),
    (
        "Support",
        "Support_Score"
    ),
    (
        "Overall Quality",
        "Overall_Conversation_Score"
    )
]


context_metrics = {

    "Romantic": [
        (
            "Romance",
            "Romance_Score"
        ),
        (
            "Emotional Connection",
            "Emotional_Connection_Score"
        ),
        (
            "Trust",
            "Trust_Score"
        ),
        (
            "Care",
            "Care_Score"
        ),
        (
            "Respect",
            "Respect_Score"
        )
    ],

    "Friendship": [
        (
            "Friendship Strength",
            "Friendship_Strength_Score"
        ),
        (
            "Trust",
            "Trust_Score"
        ),
        (
            "Support",
            "Support_Score"
        ),
        (
            "Care",
            "Care_Score"
        ),
        (
            "Respect",
            "Respect_Score"
        )
    ],

    "Professional": [
        (
            "Professionalism",
            "Professionalism_Score"
        ),
        (
            "Collaboration",
            "Collaboration_Score"
        ),
        (
            "Responsiveness",
            "Responsiveness_Score"
        )
    ],

    "Career": [
        (
            "Goal Orientation",
            "Goal_Orientation_Score"
        ),
        (
            "Support",
            "Support_Score"
        )
    ],

    "Personal Growth": [
        (
            "Goal Orientation",
            "Goal_Orientation_Score"
        ),
        (
            "Support",
            "Support_Score"
        )
    ]
}


# ============================================================
# BUILD RELEVANT METRICS
# ============================================================

metrics = [
    (
        "Conversations",
        None,
        len(filtered_df)
    )
]


# Universal metrics first
for label, column in universal_metrics:

    value = safe_mean(
        filtered_df,
        column
    )

    if value is not None:

        metrics.append(
            (
                label,
                column,
                value
            )
        )


# Context-specific metrics
if selected_context in context_metrics:

    for label, column in context_metrics[
        selected_context
    ]:

        value = safe_mean(
            filtered_df,
            column
        )

        if value is not None:

            metrics.append(
                (
                    label,
                    column,
                    value
                )
            )


# ============================================================
# KPI DISPLAY
# ============================================================

st.divider()

display_metrics = metrics[:6]

columns = st.columns(
    min(
        len(display_metrics),
        6
    )
)

for column, metric in zip(
    columns,
    display_metrics
):

    label = metric[0]
    value = metric[2]

    column.metric(
        label,
        value
    )


# ============================================================
# CONTEXT DISTRIBUTION
# ============================================================

if selected_context == "All Contexts":

    st.divider()

    st.subheader(
        "Detected Conversation Contexts"
    )

    context_counts = (
        df["Display_Context"]
        .replace("", "Unknown")
        .value_counts()
        .reset_index()
    )

    context_counts.columns = [
        "Context",
        "Conversations"
    ]

    fig_context = px.bar(
        context_counts,
        x="Context",
        y="Conversations",
        text="Conversations",
        title="AI-Detected Primary Context"
    )

    fig_context.update_layout(
        xaxis_title="Context",
        yaxis_title="Conversations",
        showlegend=False
    )

    st.plotly_chart(
        fig_context,
        use_container_width=True
    )


# ============================================================
# UNIVERSAL CONVERSATION QUALITY
# ============================================================

st.divider()

st.subheader(
    "Conversation Quality"
)

quality_metrics = []

for label, column in universal_metrics:

    value = safe_mean(
        filtered_df,
        column
    )

    if value is not None:

        quality_metrics.append(
            (
                label,
                value
            )
        )


if quality_metrics:

    quality_df = pd.DataFrame(
        quality_metrics,
        columns=[
            "Metric",
            "Score"
        ]
    )

    fig_quality = px.bar(
        quality_df,
        x="Metric",
        y="Score",
        text="Score",
        title="Universal Conversation Intelligence"
    )

    fig_quality.update_yaxes(
        range=[0, 100]
    )

    st.plotly_chart(
        fig_quality,
        use_container_width=True
    )


# ============================================================
# CONTEXT-SPECIFIC ANALYSIS
# ============================================================

if selected_context in context_metrics:

    st.divider()

    st.subheader(
        f"{selected_context} Analysis"
    )

    context_results = []

    for label, column in context_metrics[
        selected_context
    ]:

        value = safe_mean(
            filtered_df,
            column
        )

        if value is not None:

            context_results.append(
                (
                    label,
                    value
                )
            )

    if context_results:

        context_df = pd.DataFrame(
            context_results,
            columns=[
                "Metric",
                "Score"
            ]
        )

        fig_context_metrics = px.bar(
            context_df,
            x="Metric",
            y="Score",
            text="Score",
            title=f"{selected_context} Metrics"
        )

        fig_context_metrics.update_yaxes(
            range=[0, 100]
        )

        st.plotly_chart(
            fig_context_metrics,
            use_container_width=True
        )


# ============================================================
# EMOTIONAL LANDSCAPE
# ============================================================

if "Primary_Emotion" in filtered_df.columns:

    st.divider()

    st.subheader(
        "Emotional Landscape"
    )

    emotion_counts = (
        filtered_df[
            "Primary_Emotion"
        ]
        .dropna()
        .astype(str)
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .reset_index()
    )

    emotion_counts.columns = [
        "Emotion",
        "Conversations"
    ]

    if not emotion_counts.empty:

        fig_emotion = px.bar(
            emotion_counts,
            x="Emotion",
            y="Conversations",
            text="Conversations",
            title="Primary Emotional Patterns"
        )

        fig_emotion.update_layout(
            xaxis_title="Emotion",
            yaxis_title="Conversations",
            showlegend=False
        )

        st.plotly_chart(
            fig_emotion,
            use_container_width=True
        )


# ============================================================
# TOXICITY
# ============================================================

if "Toxicity_Score" in filtered_df.columns:

    toxicity_values = pd.to_numeric(
        filtered_df["Toxicity_Score"],
        errors="coerce"
    ).dropna()

    if not toxicity_values.empty:

        st.divider()

        st.subheader(
            "Conversation Health"
        )

        toxicity_df = pd.DataFrame(
            {
                "Toxicity Score":
                    toxicity_values
            }
        )

        fig_toxicity = px.histogram(
            toxicity_df,
            x="Toxicity Score",
            nbins=10,
            title="Toxicity Distribution"
        )

        fig_toxicity.update_xaxes(
            range=[0, 100]
        )

        st.plotly_chart(
            fig_toxicity,
            use_container_width=True
        )


# ============================================================
# TOPICS
# ============================================================

if "Topics" in filtered_df.columns:

    topic_values = []

    for value in filtered_df["Topics"].dropna():

        text = str(value)

        text = text.replace(
            "[",
            ""
        ).replace(
            "]",
            ""
        ).replace(
            "'",
            ""
        ).replace(
            '"',
            ""
        )

        for topic in text.split(","):

            topic = topic.strip()

            if topic:
                topic_values.append(topic)

    if topic_values:

        topic_counts = (
            pd.Series(topic_values)
            .value_counts()
            .head(15)
            .reset_index()
        )

        topic_counts.columns = [
            "Topic",
            "Count"
        ]

        st.divider()

        st.subheader(
            "Topics Discussed"
        )

        fig_topics = px.bar(
            topic_counts,
            x="Count",
            y="Topic",
            orientation="h",
            text="Count",
            title="Most Discussed Topics"
        )

        fig_topics.update_layout(
            yaxis_title="",
            xaxis_title="Conversations"
        )

        st.plotly_chart(
            fig_topics,
            use_container_width=True
        )


# ============================================================
# CONVERSATION EXPLORER
# ============================================================

st.divider()

st.subheader(
    "Conversation Explorer"
)

if "Conversation_ID" in filtered_df.columns:

    conversation_ids = (
        filtered_df[
            "Conversation_ID"
        ]
        .dropna()
        .tolist()
    )

    if conversation_ids:

        selected_id = st.selectbox(
            "Select Conversation",
            conversation_ids
        )

        selected_row = filtered_df[
            filtered_df[
                "Conversation_ID"
            ] == selected_id
        ].iloc[0]


        # ----------------------------------------------------
        # Context
        # ----------------------------------------------------

        primary_context = clean_context(
            selected_row.get(
                "Primary_Context",
                "unknown"
            )
        )

        st.info(
            f"Primary Context: {primary_context}"
        )


        secondary = get_secondary_contexts(
            selected_row
        )

        if secondary:

            st.caption(
                "Secondary Contexts: "
                + ", ".join(secondary)
            )


        # ----------------------------------------------------
        # Context confidence
        # ----------------------------------------------------

        if "Context_Confidence" in selected_row.index:

            confidence = numeric_value(
                selected_row[
                    "Context_Confidence"
                ]
            )

            if pd.notna(confidence):

                st.caption(
                    f"Context Confidence: "
                    f"{confidence:.0f}%"
                )


        # ----------------------------------------------------
        # Conversation type
        # ----------------------------------------------------

        if "Conversation_Type" in selected_row.index:

            value = selected_row[
                "Conversation_Type"
            ]

            if pd.notna(value):

                st.write(
                    "**Conversation Type:**",
                    value
                )


        # ----------------------------------------------------
        # Emotion
        # ----------------------------------------------------

        if "Primary_Emotion" in selected_row.index:

            value = selected_row[
                "Primary_Emotion"
            ]

            if pd.notna(value):

                st.write(
                    "**Primary Emotion:**",
                    value
                )


        # ----------------------------------------------------
        # Dynamic individual metrics
        # ----------------------------------------------------

        st.subheader(
            "Detected Intelligence"
        )

        individual_metrics = []


        # Universal metrics
        for label, column in universal_metrics:

            if column in selected_row.index:

                value = numeric_value(
                    selected_row[column]
                )

                if pd.notna(value):

                    individual_metrics.append(
                        (
                            label,
                            value
                        )
                    )


        # Context-specific metrics
        if primary_context in context_metrics:

            for label, column in context_metrics[
                primary_context
            ]:

                if column in selected_row.index:

                    value = numeric_value(
                        selected_row[column]
                    )

                    if pd.notna(value):

                        individual_metrics.append(
                            (
                                label,
                                value
                            )
                        )


        if individual_metrics:

            metric_columns = st.columns(
                min(
                    len(individual_metrics),
                    5
                )
            )

            for column, (
                label,
                value
            ) in zip(
                metric_columns,
                individual_metrics
            ):

                column.metric(
                    label,
                    value
                )


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        if "Summary" in selected_row.index:

            summary = selected_row[
                "Summary"
            ]

            if pd.notna(summary):

                st.subheader(
                    "AI Summary"
                )

                st.write(
                    summary
                )


        # ----------------------------------------------------
        # Relationship stage
        # Only when AI actually detected relationship context
        # ----------------------------------------------------

        relationship_contexts = [
            "Romantic",
            "Friendship",
            "Family"
        ]

        if (
            primary_context
            in relationship_contexts
            and "Relationship_Stage"
            in selected_row.index
        ):

            stage = selected_row[
                "Relationship_Stage"
            ]

            if pd.notna(stage):

                st.write(
                    "**Relationship Stage:**",
                    stage
                )


# ============================================================
# DATASET
# ============================================================

st.divider()

with st.expander(
    "View AI Analysis Dataset"
):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "WhatsApp AI • Context-Aware Conversation Intelligence • Version 1.2"
)