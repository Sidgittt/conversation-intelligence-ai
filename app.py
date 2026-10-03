import ast
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.ai.analysis_engine import AnalysisEngine
from modules.dashboard.charts import (
    emotion_chart,
    relationship_chart,
    toxicity_chart,
    conversation_type_chart,
    sufficiency_chart,
    score_distribution_chart,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Conversation Intelligence AI",
    page_icon="🧠",
    layout="wide",
)


# ============================================================
# FILE PATHS
# ============================================================

CHAT_FILE = Path("data") / "WhatsApp Chat with XYZ.txt"
OUTPUT_FILE = Path("output") / "ai_analysis.csv"


# ============================================================
# METRICS
# ============================================================

UNIVERSAL_METRICS = [
    ("Communication", "Communication_Score"),
    ("Engagement", "Quality_Engagement_Score"),
    ("Positivity", "Quality_Positivity_Score"),
    ("Emotional Depth", "Quality_Emotional_Depth_Score"),
    ("Clarity", "Quality_Clarity_Score"),
    ("Conflict", "Conflict_Score"),
    ("Support", "Support_Score"),
    ("Conversation Quality", "Conversation_Quality_Score"),
]

CONTEXT_METRICS = {
    "romantic": [
        ("Romance", "Romance_Score"),
        ("Care", "Care_Score"),
        ("Trust", "Trust_Score"),
        ("Communication", "Communication_Score"),
        ("Emotional Depth", "Quality_Emotional_Depth_Score"),
        ("Conflict", "Conflict_Score"),
    ],
    "friendship": [
        ("Friendship", "Friendship_Score"),
        ("Trust", "Trust_Score"),
        ("Communication", "Communication_Score"),
        ("Support", "Support_Score"),
        ("Positivity", "Quality_Positivity_Score"),
    ],
    "casual": [
        ("Communication", "Communication_Score"),
        ("Engagement", "Quality_Engagement_Score"),
        ("Positivity", "Quality_Positivity_Score"),
        ("Clarity", "Quality_Clarity_Score"),
    ],
    "emotional_support": [
        ("Care", "Care_Score"),
        ("Support", "Support_Score"),
        ("Emotional Depth", "Quality_Emotional_Depth_Score"),
        ("Trust", "Trust_Score"),
    ],
    "conflict": [
        ("Conflict", "Conflict_Score"),
        ("Communication", "Communication_Score"),
        ("Clarity", "Quality_Clarity_Score"),
        ("Emotional Depth", "Quality_Emotional_Depth_Score"),
    ],
}


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
        .main-title { font-size:42px; font-weight:800; color:#172b4d; margin-bottom:5px; }
        .subtitle { font-size:18px; color:#68758a; margin-bottom:30px; }
        .context-badge { display:inline-block; padding:8px 14px; margin-right:8px; margin-bottom:8px; border-radius:8px; background:#eef0f4; color:#26364d; font-size:15px; }
        .section-title { font-size:25px; font-weight:650; color:#172b4d; margin-top:20px; margin-bottom:15px; }

        .portal {
            position:relative;
            overflow:hidden;
            min-height:405px;
            padding:44px 46px;
            border-radius:30px;
            margin-bottom:30px;
            background:
                radial-gradient(circle at 78% 45%, rgba(0,220,255,.20), transparent 16%),
                radial-gradient(circle at 88% 18%, rgba(161,78,255,.30), transparent 23%),
                radial-gradient(circle at 67% 85%, rgba(255,76,171,.16), transparent 24%),
                linear-gradient(135deg,#070b21 0%,#10183d 48%,#172d58 100%);
            box-shadow:0 22px 55px rgba(9,18,53,.28);
        }

        .portal:before {
            content:"";
            position:absolute;
            width:390px;
            height:390px;
            right:-55px;
            top:-5px;
            border-radius:50%;
            border:1px solid rgba(113,220,255,.28);
            box-shadow:
                0 0 0 32px rgba(113,220,255,.035),
                0 0 0 75px rgba(113,220,255,.025),
                0 0 0 120px rgba(113,220,255,.018);
        }

        .portal:after {
            content:"";
            position:absolute;
            width:8px;
            height:8px;
            right:210px;
            top:72px;
            border-radius:50%;
            background:#75e9ff;
            box-shadow:
                70px 90px 0 #c17cff,
                -90px 175px 0 #ff78c8,
                145px 185px 0 #75e9ff,
                35px -35px 0 #ffffff;
        }

        .portal-kicker {
            position:relative;
            z-index:2;
            color:#72e4ff;
            font-size:11px;
            font-weight:800;
            letter-spacing:3px;
            text-transform:uppercase;
            margin-bottom:22px;
        }

        .portal h1 {
            position:relative;
            z-index:2;
            color:#ffffff;
            font-size:50px;
            line-height:1.03;
            letter-spacing:-1.5px;
            max-width:650px;
            margin:0;
        }

        .portal h1 .pink { color:#ff83c9; }
        .portal h1 .blue { color:#75e9ff; }

        .portal-copy {
            position:relative;
            z-index:2;
            max-width:570px;
            color:#b8c8e5;
            font-size:15px;
            line-height:1.7;
            margin-top:22px;
        }

        .signal-cloud {
            position:absolute;
            z-index:2;
            right:34px;
            bottom:38px;
            width:330px;
            display:flex;
            flex-wrap:wrap;
            justify-content:center;
            gap:10px;
        }

        .signal {
            padding:10px 15px;
            border-radius:14px;
            color:#f4fbff;
            background:rgba(255,255,255,.07);
            border:1px solid rgba(255,255,255,.16);
            backdrop-filter:blur(8px);
            font-size:12px;
            font-weight:800;
            letter-spacing:1px;
        }

        .signal:nth-child(2), .signal:nth-child(5) {
            color:#ff9bd4;
            border-color:rgba(255,131,201,.35);
        }

        .signal:nth-child(3), .signal:nth-child(6) {
            color:#8cecff;
            border-color:rgba(117,233,255,.35);
        }

        .home-heading {
            color:#172b4d;
            font-size:24px;
            font-weight:800;
            margin:8px 0 15px;
        }

        .home-card {
            padding:22px;
            border:1px solid #e2eaf4;
            border-radius:17px;
            background:#ffffff;
            min-height:145px;
            box-shadow:0 5px 18px rgba(30,50,80,.06);
        }

        .home-card h3 { margin:0 0 8px; color:#172b4d; font-size:19px; }
        .home-card p { margin:0; color:#68758a; line-height:1.5; font-size:14px; }

        .mini-label {
            color:#8392aa;
            font-size:11px;
            font-weight:800;
            letter-spacing:1.5px;
            text-transform:uppercase;
            margin-bottom:7px;
        }

        .status-box {
            padding:18px 20px;
            border-radius:16px;
            background:#f4f8fc;
            border:1px solid #e1eaf3;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):
    if value is None:
        return None

    if pd.isna(value):
        return None

    if isinstance(value, str):

        value = value.strip()

        if not value:
            return None

        if value.lower() in {
            "nan",
            "none",
            "null",
        }:
            return None

    return value


def display_value(value, default="Not available"):
    value = clean_value(value)

    if value is None:
        return default

    return str(value)


def format_label(value):
    value = display_value(value)

    return (
        value
        .replace("_", " ")
        .replace("-", " ")
        .title()
    )


def normalize_context(value):
    value = clean_value(value)

    if value is None:
        return None

    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def get_numeric_value(value):
    value = clean_value(value)

    if value is None:
        return None

    try:
        return float(value)
    except Exception:
        return None


def get_average(dataframe, column):
    if column not in dataframe.columns:
        return None

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return round(float(values.mean()), 1)


def get_first_existing_column(dataframe, candidates):
    for column in candidates:
        if column in dataframe.columns:
            return column

    return None


def get_context_column(dataframe):
    return get_first_existing_column(
        dataframe,
        [
            "Primary_Context",
            "primary_context",
            "Context",
            "context",
            "Conversation_Context",
            "conversation_context",
        ],
    )


def get_context_values(dataframe):
    context_column = get_context_column(dataframe)

    if context_column is None:
        return []

    contexts = []

    for value in dataframe[context_column].dropna().unique():

        normalized = normalize_context(value)

        if normalized and normalized not in contexts:
            contexts.append(normalized)

    return sorted(contexts)


def get_metrics_for_context(context):
    normalized = normalize_context(context)

    if normalized in CONTEXT_METRICS:
        return CONTEXT_METRICS[normalized]

    return UNIVERSAL_METRICS


# ============================================================
# DATA LOADING
# ============================================================

def load_analysis_results():
    if not OUTPUT_FILE.exists():
        return None

    try:

        dataframe = pd.read_csv(OUTPUT_FILE)

        if dataframe.empty:
            return None

        return dataframe

    except Exception as error:

        st.error(
            f"Unable to read AI analysis output: {error}"
        )

        return None


@st.cache_data
def load_prepared_data():

    if not CHAT_FILE.exists():
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            {},
        )

    try:

        engine = AnalysisEngine(
            chat_file=str(CHAT_FILE)
        )

        result = engine.prepare()

        messages = result.get(
            "messages",
            pd.DataFrame(),
        )

        conversations = result.get(
            "conversations",
            pd.DataFrame(),
        )

        profile = result.get(
            "profile",
            {},
        )

        return (
            messages,
            conversations,
            profile,
        )

    except Exception as error:

        st.error(
            f"Unable to load prepared data: {error}"
        )

        return (
            pd.DataFrame(),
            pd.DataFrame(),
            {},
        )


def save_uploaded_file(uploaded_file):

    CHAT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CHAT_FILE.write_bytes(
        uploaded_file.getbuffer()
    )

    st.cache_data.clear()


# ============================================================
# DISPLAY HELPERS
# ============================================================

def render_metric_cards(dataframe, metrics):

    columns = st.columns(len(metrics))

    for index, metric in enumerate(metrics):

        label, column = metric

        value = get_average(
            dataframe,
            column,
        )

        with columns[index]:

            if value is None:

                st.metric(
                    label,
                    "Not available",
                )

            else:

                st.metric(
                    label,
                    value,
                )


def display_context_badges(dataframe):

    contexts = get_context_values(dataframe)

    if not contexts:
        return

    st.markdown(
        "### Detected Conversation Contexts"
    )

    badges = ""

    for context in contexts:

        display_name = (
            context
            .replace("_", " ")
            .title()
        )

        badges += (
            f'<span class="context-badge">'
            f'{display_name}'
            f'</span>'
        )

    st.markdown(
        badges,
        unsafe_allow_html=True,
    )


def parse_list_value(value):

    value = clean_value(value)

    if value is None:
        return []

    if isinstance(value, list):
        return value

    try:

        parsed = ast.literal_eval(str(value))

        if isinstance(parsed, list):
            return parsed

    except Exception:
        pass

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


def render_list_items(value, empty_message):

    items = parse_list_value(value)

    if not items:

        st.info(empty_message)

        return

    for item in items:
        st.markdown(f"- {item}")


def render_flags(value, title, icon):

    items = parse_list_value(value)

    st.markdown(
        f"#### {icon} {title}"
    )

    if not items:

        st.info(
            f"No {title.lower()} detected."
        )

        return

    for item in items:
        st.markdown(f"- {item}")


def render_important_moments(value):

    value = clean_value(value)

    if value is None:

        st.info(
            "No important moments detected."
        )

        return

    try:

        parsed = ast.literal_eval(str(value))

        if isinstance(parsed, list):

            for item in parsed:

                if isinstance(item, dict):

                    moment_type = item.get(
                        "type",
                        "Moment",
                    )

                    description = item.get(
                        "description",
                        "",
                    )

                    st.markdown(
                        f"**{format_label(moment_type)}:** "
                        f"{description}"
                    )

                else:

                    st.markdown(f"- {item}")

            return

    except Exception:
        pass

    st.write(value)


def render_quotes(value):

    quotes = parse_list_value(value)

    if not quotes:

        st.info(
            "No memorable quotes detected."
        )

        return

    for quote in quotes:
        st.markdown(f"> {quote}")


def render_conversation_flags(row):

    flag_columns = [
        "Argument",
        "Apology",
        "Future_Planning",
        "Family_Discussion",
        "Marriage_Discussion",
        "Financial_Discussion",
        "Career_Discussion",
        "Late_Reply_After_Serious_Chat",
        "Ghosting",
        "Double_Texting",
        "Silent_Treatment",
        "Sexting",
        "Meeting_Planned",
        "Compliment",
        "Support_During_Difficult_Time",
    ]

    active_flags = []

    for column in flag_columns:

        value = clean_value(
            row.get(column)
        )

        if isinstance(value, str):

            is_true = value.lower() in {
                "true",
                "yes",
                "1",
            }

        else:

            is_true = (
                value is True
                or value == 1
            )

        if is_true:
            active_flags.append(
                format_label(column)
            )

    if not active_flags:
        return

    st.markdown(
        "#### Conversation Flags"
    )

    for flag in active_flags:
        st.markdown(f"- {flag}")


def render_toxicity_details(row):

    toxicity_columns = [
        "Toxicity_Score",
        "Toxicity_Level",
        "Toxicity_Evidence",
        "Toxicity_Explanation",
    ]

    available_columns = [
        column
        for column in toxicity_columns
        if column in row.index
    ]

    if not available_columns:
        return

    toxicity_data = {}

    for column in available_columns:

        value = clean_value(
            row.get(column)
        )

        if value is not None:
            toxicity_data[
                format_label(column)
            ] = value

    if not toxicity_data:
        return

    st.markdown(
        "#### Toxicity Details"
    )

    st.json(toxicity_data)


# ============================================================
# CONVERSATION HELPERS
# ============================================================

def get_conversation_id_column(dataframe):

    return get_first_existing_column(
        dataframe,
        [
            "Conversation_ID",
            "conversation_id",
            "Conversation",
            "conversation",
            "Conversation_Index",
            "conversation_index",
            "Group_ID",
            "group_id",
        ],
    )


def get_message_rows_for_conversation(
    messages,
    conversation_id,
):

    if messages is None or messages.empty:
        return pd.DataFrame()

    conversation_column = (
        get_conversation_id_column(messages)
    )

    if conversation_column is None:
        return messages.copy()

    return messages[
        messages[conversation_column].astype(str)
        == str(conversation_id)
    ].copy()


def get_conversation_row(
    dataframe,
    conversation_id,
):

    if dataframe is None or dataframe.empty:
        return None

    conversation_column = (
        get_conversation_id_column(dataframe)
    )

    if conversation_column is None:
        return None

    matching_rows = dataframe[
        dataframe[conversation_column].astype(str)
        == str(conversation_id)
    ]

    if matching_rows.empty:
        return None

    return matching_rows.iloc[0]


# ============================================================
# HOME PAGE
# ============================================================

def render_home():
    messages, conversations, profile = load_prepared_data()
    results = load_analysis_results()

    total_messages = len(messages) if messages is not None else 0
    total_conversations = len(conversations) if conversations is not None else 0
    participants = profile.get("participants", []) if isinstance(profile, dict) else []
    total_participants = len(participants)

    analyzed_count = len(results) if results is not None else 0
    remaining_count = max(total_conversations - analyzed_count, 0)
    coverage = round((analyzed_count / total_conversations) * 100, 1) if total_conversations else 0

    st.markdown(
        """
        <div class="portal">
            <div class="portal-kicker">CONVERSATION INTELLIGENCE · AI LAB</div>
            <h1>From messages to <span class="blue">insights.</span></h1>
            <div class="portal-copy">
                Enter your conversation intelligence workspace.
                Discover what is being said, what is being felt,
                and what the evidence actually supports.
            </div>
            <div class="signal-cloud">
                <span class="signal">EMOTION</span>
                <span class="signal">CONTEXT</span>
                <span class="signal">INTENT</span>
                <span class="signal">PATTERNS</span>
                <span class="signal">DYNAMICS</span>
                <span class="signal">EVIDENCE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    upload_col, status_col = st.columns([1.35, 1])

    with upload_col:
        st.markdown('<div class="home-heading">Enter your conversation</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload a WhatsApp exported text file",
            type=["txt"],
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            save_uploaded_file(uploaded_file)
            st.success(f"Uploaded: {uploaded_file.name}")

    with status_col:
        st.markdown('<div class="home-heading">Workspace signal</div>', unsafe_allow_html=True)
        if CHAT_FILE.exists():
            st.markdown(
                f'<div class="status-box"><b>🟢 Conversation file ready</b><br><span style="color:#68758a;font-size:13px;">{CHAT_FILE.stat().st_size / 1024:.1f} KB stored locally</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Upload a conversation file to begin.")

    if not CHAT_FILE.exists():
        st.markdown(
            '<div class="home-card"><div class="mini-label">YOUR PRIVATE AI LAB</div><h3>Start with a conversation</h3><p>Upload a WhatsApp TXT export to activate the intelligence workspace.</p></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="home-heading">Live workspace</div>', unsafe_allow_html=True)
    metric_cols = st.columns(4)
    metric_cols[0].metric("💬 Messages", f"{total_messages:,}")
    metric_cols[1].metric("🧩 Conversations", f"{total_conversations:,}")
    metric_cols[2].metric("👥 Participants", f"{total_participants:,}")
    metric_cols[3].metric("📊 Coverage", f"{coverage}%")

    st.markdown('<div class="home-heading">What the AI looks for</div>', unsafe_allow_html=True)
    cards = st.columns(4)
    concepts = [
        ("💗", "Emotion", "What feelings and emotional shifts appear?"),
        ("🧩", "Context", "What is this conversation really about?"),
        ("〰️", "Patterns", "What repeats across conversations?"),
        ("◈", "Evidence", "What can be supported by actual messages?"),
    ]
    for column, (icon, title, description) in zip(cards, concepts):
        with column:
            st.markdown(
                f'<div class="home-card"><div style="font-size:28px;margin-bottom:10px;">{icon}</div><h3>{title}</h3><p>{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="home-heading">Analysis progress</div>', unsafe_allow_html=True)
    progress_col, action_col = st.columns([1.5, 1])
    with progress_col:
        st.progress(min(coverage / 100, 1.0))
        st.write(f"**{analyzed_count}** conversations analysed · **{remaining_count}** remaining")
    with action_col:
        if st.button("⚙️ Prepare Conversation", use_container_width=True):
            with st.spinner("Preparing conversation data..."):
                try:
                    load_prepared_data.clear()
                    load_prepared_data()
                    st.success("Conversation prepared successfully.")
                    st.rerun()
                except Exception as error:
                    st.error(f"Unable to prepare conversation: {error}")

    st.markdown('<div class="home-heading">Enter the intelligence workspace</div>', unsafe_allow_html=True)
    feature_cols = st.columns(4)
    features = [
        ("📈", "Dashboard", "See the big picture."),
        ("🔎", "Explorer", "Inspect the actual messages."),
        ("🗂️", "Conversation Data", "Understand the prepared data."),
        ("🤖", "AI Assistant", "Ask questions about your results."),
    ]
    for column, (icon, title, description) in zip(feature_cols, features):
        with column:
            st.markdown(
                f'<div class="home-card"><div style="font-size:25px;margin-bottom:10px;">{icon}</div><h3>{title}</h3><p>{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="home-heading">Recent conversation preview</div>', unsafe_allow_html=True)
    if conversations is not None and not conversations.empty:
        st.dataframe(conversations.head(5), use_container_width=True, hide_index=True)
    else:
        st.info("Prepare the conversation to see conversation groups here.")

    st.markdown('<div class="home-heading">Run AI analysis</div>', unsafe_allow_html=True)
    st.caption("Start with one conversation first to verify the AI output.")
    analysis_limit = st.number_input(
        "Number of conversations to analyse",
        min_value=1,
        max_value=100,
        value=1,
        step=1,
    )
    if st.button("🚀 Run AI Analysis", type="primary", use_container_width=True):
        with st.spinner("Analysing conversations with AI..."):
            try:
                engine = AnalysisEngine(chat_file=str(CHAT_FILE))
                result = engine.run(limit=int(analysis_limit), force_reanalysis=False)
                st.cache_data.clear()
                st.success("AI analysis completed successfully.")
                result_cols = st.columns(4)
                result_cols[0].metric("Messages", result["messages"])
                result_cols[1].metric("Conversations", result["conversations"])
                result_cols[2].metric("Successful", result["successful"])
                result_cols[3].metric("Failed", result["failed"])
                if result["skipped"] > 0:
                    st.info(f"Skipped existing results: {result['skipped']}")
                st.info("Open Dashboard or Conversation Explorer to view the results.")
            except Exception as error:
                st.error(f"AI analysis failed: {error}")


# ============================================================
# DASHBOARD PAGE
# ============================================================

def render_dashboard():

    st.markdown(
        '<div class="main-title">Conversation Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">Explore conversation patterns, emotions, quality and evidence-supported insights.</div>',
        unsafe_allow_html=True,
    )

    dataframe = load_analysis_results()

    if dataframe is None:
        st.warning("No AI analysis results found.")
        st.info("Go to Home and run AI analysis first.")
        return

    # Always work on a clean copy and never treat missing scores as zero.
    df = dataframe.copy()

    st.markdown("### Analysis Overview")

    total = len(df)
    sufficient = 0
    limited = 0
    insufficient = 0

    if "Conversation_Sufficiency" in df.columns:
        sufficiency = df["Conversation_Sufficiency"].astype(str).str.lower()
        sufficient = int((sufficiency == "sufficient").sum())
        limited = int((sufficiency == "limited").sum())
        insufficient = int((sufficiency == "insufficient").sum())

    analyzed = total - insufficient
    coverage = round((analyzed / total) * 100, 1) if total else 0

    cards = st.columns(5)
    cards[0].metric("Analysed Conversations", total)
    cards[1].metric("Sufficient Evidence", sufficient)
    cards[2].metric("Limited Evidence", limited)
    cards[3].metric("Insufficient Evidence", insufficient)
    cards[4].metric("Analysis Coverage", f"{coverage}%")

    if insufficient:
        st.info(
            f"{insufficient} conversation(s) do not contain enough evidence for reliable scoring. "
            "Those scores are intentionally excluded from averages."
        )

    st.divider()

    st.markdown("### Conversation Landscape")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if "Primary_Emotion" in df.columns:
            st.plotly_chart(emotion_chart(df), use_container_width=True)
        else:
            st.info("Emotion data is not available.")

    with chart_col2:
        if "Conversation_Type" in df.columns:
            st.plotly_chart(conversation_type_chart(df), use_container_width=True)
        else:
            st.info("Conversation type data is not available.")

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        if "Conversation_Sufficiency" in df.columns:
            st.plotly_chart(sufficiency_chart(df), use_container_width=True)
        else:
            st.info("Evidence classification is not available.")

    with chart_col4:
        if "Toxicity_Level" in df.columns:
            st.plotly_chart(toxicity_chart(df), use_container_width=True)
        else:
            st.info("Toxicity data is not available.")

    st.divider()

    st.markdown("### Evidence-Supported Scores")

    relationship_columns = [
        "Trust_Score",
        "Communication_Score",
        "Care_Score",
        "Respect_Score",
        "Romance_Score",
        "Friendship_Score",
    ]

    available_relationship_columns = [
        column for column in relationship_columns if column in df.columns
    ]

    if available_relationship_columns:
        score_df = df[available_relationship_columns].apply(
            pd.to_numeric, errors="coerce"
        )

        if score_df.notna().any().any():
            st.plotly_chart(
                relationship_chart(df),
                use_container_width=True,
            )
            st.plotly_chart(
                score_distribution_chart(df),
                use_container_width=True,
            )
        else:
            st.info("No relationship scores have enough evidence yet.")
    else:
        st.info("Relationship score columns are not available.")

    st.divider()

    st.markdown("### Universal Communication Metrics")
    render_metric_cards(df, UNIVERSAL_METRICS)

    st.divider()

    contexts = get_context_values(df)

    if contexts:
        context_options = [
            "All Contexts",
            *[context.replace("_", " ").title() for context in contexts],
        ]

        selected_context = st.selectbox(
            "Filter by conversation context",
            context_options,
        )

        if selected_context == "All Contexts":
            filtered_dataframe = df
            selected_context_key = None
        else:
            selected_context_key = normalize_context(selected_context)
            context_column = get_context_column(df)
            filtered_dataframe = df[
                df[context_column].apply(normalize_context)
                == selected_context_key
            ]

        st.markdown(f"### {selected_context} Insights")
        render_metric_cards(
            filtered_dataframe,
            get_metrics_for_context(selected_context_key),
        )
    else:
        filtered_dataframe = df
        st.info("No explicit context labels were found.")

    st.divider()

    st.markdown("### Conversation Results")

    summary_columns = [
        "Conversation_ID",
        "Conversation_Sufficiency",
        "Primary_Context",
        "Primary_Emotion",
        "Conversation_Type",
        "Summary",
        "Confidence",
    ]

    available_summary_columns = [
        column for column in summary_columns if column in filtered_dataframe.columns
    ]

    if available_summary_columns:
        st.dataframe(
            filtered_dataframe[available_summary_columns],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No conversation summary columns are available.")


# ============================================================
# CONVERSATION EXPLORER PAGE
# ============================================================

def render_conversation_explorer():

    st.markdown(
        '<div class="main-title">'
        "Conversation Explorer"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "Explore one conversation using its actual messages "
        "and existing AI analysis."
        "</div>",
        unsafe_allow_html=True,
    )

    analysis_dataframe = load_analysis_results()

    if analysis_dataframe is None:

        st.warning(
            "No AI analysis results found."
        )

        return

    messages, conversations, profile = (
        load_prepared_data()
    )

    analysis_id_column = get_conversation_id_column(
        analysis_dataframe
    )

    if analysis_id_column is None:

        st.error(
            "Conversation_ID column was not found "
            "in the AI analysis output."
        )

        return

    conversation_ids = (
        analysis_dataframe[analysis_id_column]
        .dropna()
        .unique()
        .tolist()
    )

    if not conversation_ids:

        st.info(
            "No conversations are available."
        )

        return

    conversation_ids = sorted(
        conversation_ids,
        key=lambda value: str(value),
    )

    selected_id = st.selectbox(
        "Select Conversation",
        conversation_ids,
    )

    selected_row = get_conversation_row(
        analysis_dataframe,
        selected_id,
    )

    if selected_row is None:

        st.error(
            "Unable to find the selected conversation."
        )

        return

    conversation_messages = (
        get_message_rows_for_conversation(
            messages,
            selected_id,
        )
    )

    st.divider()

    st.markdown(
        f"### Conversation {display_value(selected_id)}"
    )

    start_time = selected_row.get(
        "Start_Time",
        selected_row.get(
            "Start",
            None,
        ),
    )

    end_time = selected_row.get(
        "End_Time",
        selected_row.get(
            "End",
            None,
        ),
    )

    duration = selected_row.get(
        "Duration_Minutes",
        None,
    )

    participants = selected_row.get(
        "Participants",
        None,
    )

    primary_context = selected_row.get(
        "Primary_Context",
        selected_row.get(
            "Context",
            "Unknown",
        ),
    )

    message_count = len(
        conversation_messages
    )

    if message_count == 0:

        message_count = selected_row.get(
            "Message_Count",
            selected_row.get(
                "Messages",
                "Not available",
            ),
        )

    columns = st.columns(4)

    with columns[0]:

        st.metric(
            "Messages",
            display_value(message_count),
        )

    with columns[1]:

        duration_value = get_numeric_value(
            duration
        )

        if duration_value is not None:

            duration_text = (
                f"{duration_value:.1f} minutes"
            )

        else:

            duration_text = display_value(
                duration,
                "Not available",
            )

        st.metric(
            "Duration",
            duration_text,
        )

    with columns[2]:

        st.metric(
            "Participants",
            display_value(
                participants,
                "Not available",
            ),
        )

    with columns[3]:

        st.metric(
            "Primary Context",
            format_label(primary_context),
        )

    st.divider()

    st.markdown(
        "### Conversation Scores"
    )

    score_columns = [
        column
        for column in selected_row.index
        if column.endswith("_Score")
        and "Toxicity" not in column
    ]

    score_rows = []

    for column in score_columns:

        value = clean_value(
            selected_row[column]
        )

        if value is None:
            continue

        score_rows.append(
            {
                "Metric": format_label(column),
                "Score": display_value(value),
            }
        )

    if score_rows:

        st.dataframe(
            pd.DataFrame(score_rows),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No conversation scores are available."
        )

    st.divider()

    st.markdown(
        "### Conversation Summary"
    )

    summary = selected_row.get(
        "Summary",
        None,
    )

    st.write(
        display_value(
            summary,
            "No summary is available.",
        )
    )

    st.markdown(
        "### Topics"
    )

    render_list_items(
        selected_row.get(
            "Topics",
            None,
        ),
        "No topics were detected.",
    )

    st.markdown(
        "### Conversation Observations"
    )

    observation_columns = st.columns(2)

    with observation_columns[0]:

        render_flags(
            selected_row.get(
                "Green_Flags",
                None,
            ),
            "Green Flags",
            "🟢",
        )

    with observation_columns[1]:

        render_flags(
            selected_row.get(
                "Red_Flags",
                None,
            ),
            "Red Flags",
            "🔴",
        )

    st.markdown(
        "#### Important Moments"
    )

    render_important_moments(
        selected_row.get(
            "Important_Moments",
            None,
        )
    )

    st.markdown(
        "#### Memorable Quotes"
    )

    render_quotes(
        selected_row.get(
            "Memorable_Quotes",
            None,
        )
    )

    render_conversation_flags(
        selected_row
    )

    render_toxicity_details(
        selected_row
    )

    st.divider()

    st.markdown(
        "### Message History"
    )

    if conversation_messages.empty:

        st.info(
            "Actual messages for this conversation "
            "were not found."
        )

    else:

        st.dataframe(
            conversation_messages,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# CONVERSATION DATA PAGE
# ============================================================

def render_conversation_data():

    st.markdown(
        '<div class="main-title">'
        "Conversation Data"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "View the prepared conversation data."
        "</div>",
        unsafe_allow_html=True,
    )

    if not CHAT_FILE.exists():

        st.info(
            "Upload a conversation file from the Home page first."
        )

        return

    messages, conversations, profile = (
        load_prepared_data()
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Messages",
            "Conversations",
            "Profile",
        ]
    )

    with tab1:

        st.subheader("Messages")

        if messages.empty:

            st.info(
                "No prepared messages are available."
            )

        else:

            st.dataframe(
                messages,
                use_container_width=True,
                hide_index=True,
            )

    with tab2:

        st.subheader("Conversation Groups")

        if conversations.empty:

            st.info(
                "No conversation groups are available."
            )

        else:

            st.dataframe(
                conversations,
                use_container_width=True,
                hide_index=True,
            )

    with tab3:

        st.subheader("Conversation Profile")

        participants = profile.get(
            "participants",
            [],
        )

        st.json(
            {
                "participants": participants,
                **{
                    key: value
                    for key, value in profile.items()
                    if key != "participants"
                },
            }
        )


# ============================================================
# AI ASSISTANT PAGE
# ============================================================

def render_ai_assistant():
    st.markdown(
        '<div class="main-title">AI Assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "Ask questions across your analyzed conversation history."
        "</div>",
        unsafe_allow_html=True,
    )

    analysis_dataframe = load_analysis_results()

    if analysis_dataframe is None or analysis_dataframe.empty:
        st.warning("No AI analysis results found.")
        st.info("Run AI analysis first from the Home page.")
        return

    # Load the prepared raw messages as the second evidence source.
    # The longitudinal assistant searches both analyzed results and
    # the actual prepared conversation messages.
    messages, _, _ = load_prepared_data()

    st.markdown(
        """
        <div class="home-card">
            <div class="mini-label">LONGITUDINAL INTELLIGENCE</div>
            <h3>Ask about patterns across your conversation history</h3>
            <p>
                The assistant can retrieve relevant conversations, use their
                dates and analysis together, and reason about changes over time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "Ask a question",
        placeholder=(
            "Try: How has our communication changed over time?\n"
            "Try: When did conflicts become more frequent?\n"
            "Try: What patterns appear across our conversations?"
        ),
        key="assistant_question",
        height=130,
    )

    if st.button("🤖 Ask Assistant", type="primary"):
        if not question.strip():
            st.warning("Please enter a question first.")
            return

        try:
            from modules.agent.agent import ConversationAgent

            with st.spinner("Retrieving conversation history and reasoning over the evidence..."):
                assistant = ConversationAgent(analysis_dataframe, messages)
                result = assistant.ask(question.strip())

            st.markdown("### Answer")
            st.markdown(result["answer"])

            st.markdown("### Evidence used")
            st.caption(
                f"Retrieved {result['evidence_count']} relevant conversation(s) "
                f"for this answer."
            )

            evidence_df = result["evidence"]

            if not evidence_df.empty:
                display_columns = [
                    column
                    for column in [
                        "Conversation_ID",
                        "Start_Time",
                        "End_Time",
                        "Primary_Context",
                        "Primary_Emotion",
                        "Topics",
                        "Summary",
                        "Search_Score",
                        "Evidence_Source",
                    ]
                    if column in evidence_df.columns
                ]

                st.dataframe(
                    evidence_df[display_columns],
                    use_container_width=True,
                    hide_index=True,
                )

        except Exception as error:
            st.error(f"Unable to answer the question: {error}")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🧠 Conversation Intelligence AI"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Dashboard",
        "Conversation Explorer",
        "Conversation Data",
        "AI Assistant",
    ],
)

st.sidebar.divider()

st.sidebar.caption(
    "Analyze conversations using adaptive, "
    "context-aware AI insights."
)


# ============================================================
# PAGE ROUTING
# ============================================================

if page == "Home":

    render_home()

elif page == "Dashboard":

    render_dashboard()

elif page == "Conversation Explorer":

    render_conversation_explorer()

elif page == "Conversation Data":

    render_conversation_data()

elif page == "AI Assistant":

    render_ai_assistant()