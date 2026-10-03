import streamlit as st
import plotly.express as px
from pathlib import Path

from parser import WhatsAppParser
from cleaner import ChatCleaner
from conversation import ConversationEngine
from analytics import ChatAnalytics

st.set_page_config(
    page_title="WhatsApp.ai",
    layout="wide"
)

st.title("📱 WhatsApp.ai")

# ==========================
# LOAD DATA
# ==========================

CHAT_FILE = Path("data") / "WhatsApp Chat with XYZ.txt"

parser = WhatsAppParser(CHAT_FILE)
df = parser.parse_messages()

df = ChatCleaner(df).clean()

df = ConversationEngine(df, gap_minutes=240).build()

analytics = ChatAnalytics(df)
df = analytics.build()

# ==========================
# SIDEBAR
# ==========================

st.sidebar.title("Filters")

participants = ["All"] + sorted(df["Sender"].unique().tolist())

selected_sender = st.sidebar.selectbox(
    "Participant",
    participants
)

min_date = df["Datetime"].min().date()
max_date = df["Datetime"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df.copy()

if selected_sender != "All":
    filtered_df = filtered_df[
        filtered_df["Sender"] == selected_sender
    ]

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Datetime"].dt.date >= start_date) &
        (filtered_df["Datetime"].dt.date <= end_date)
    ]

summary = ChatAnalytics(filtered_df).summary()

# ==========================
# KPI
# ==========================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Messages", len(filtered_df))
col2.metric("Participants", filtered_df["Sender"].nunique())
col3.metric("Conversations", summary["Total_Conversations"])
col4.metric("Largest Conversation", summary["Largest_Conversation"])

st.divider()

# ==========================
# DATA PREVIEW
# ==========================

with st.expander("View Dataset"):
    st.dataframe(filtered_df)

# ==========================
# MESSAGES PER PERSON
# ==========================

st.subheader("Messages per Person")

msg_count = (
    filtered_df.groupby("Sender")
      .size()
      .reset_index(name="Messages")
      .sort_values("Messages", ascending=False)
)

fig = px.bar(
    msg_count,
    x="Sender",
    y="Messages",
    text="Messages"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================
# DAILY ACTIVITY
# ==========================

st.subheader("Daily Activity")

daily = (
    filtered_df.groupby("Date")
      .size()
      .reset_index(name="Messages")
)

fig = px.line(
    daily,
    x="Date",
    y="Messages",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# ==========================
# MONTHLY ACTIVITY
# ==========================

st.subheader("Monthly Activity")

monthly = (
    filtered_df
    .groupby(["Year", "Month", "Month_Name"])
    .size()
    .reset_index(name="Messages")
)

monthly["Label"] = (
    monthly["Month_Name"] + " " +
    monthly["Year"].astype(str)
)

fig = px.line(
    monthly,
    x="Label",
    y="Messages",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# ==========================
# HOURLY ACTIVITY
# ==========================

st.subheader("Hourly Activity")

hourly = (
    filtered_df
    .groupby("Hour")
    .size()
    .reset_index(name="Messages")
)

fig = px.bar(
    hourly,
    x="Hour",
    y="Messages",
    text="Messages"
)

fig.update_layout(
    xaxis=dict(
        tickmode="linear",
        dtick=1
    )
)

st.plotly_chart(fig, use_container_width=True)