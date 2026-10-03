
"""
analytics.py
Response Analytics Engine v1
"""

import pandas as pd


class ChatAnalytics:

    def __init__(self, df: pd.DataFrame):
        self.df = df.sort_values("Datetime").reset_index(drop=True).copy()

    def build(self) -> pd.DataFrame:

        self.df["Previous_Sender"] = self.df["Sender"].shift(1)
        self.df["Previous_Time"] = self.df["Datetime"].shift(1)

        self.df["Reply_Time_Minutes"] = (
            (self.df["Datetime"] - self.df["Previous_Time"])
            .dt.total_seconds()
            .div(60)
        )

        self.df["Is_Reply"] = (
            self.df["Sender"] != self.df["Previous_Sender"]
        )

        self.df["Is_Double_Text"] = (
            self.df["Sender"] == self.df["Previous_Sender"]
        )

        return self.df

    def summary(self):

        df = self.df

        reply = (
            df[df["Is_Reply"]]
            .groupby("Sender")["Reply_Time_Minutes"]
            .mean()
            .round(2)
        )

        double = (
            df[df["Is_Double_Text"]]
            .groupby("Sender")
            .size()
        )

        starter = (
            df[df["Conversation_Start"]]
            .groupby("Started_By")
            .size()
        )

        ender = (
            df[df["Conversation_End"]]
            .groupby("Ended_By")
            .size()
        )

        return {
            "Average_Reply_Time": reply,
            "Double_Text_Count": double,
            "Conversation_Starters": starter,
            "Conversation_Enders": ender,
            "Total_Conversations": df["Conversation_ID"].nunique(),
            "Largest_Conversation": int(df["Conversation_Size"].max()),
            "Average_Conversation_Size": round(
                df["Conversation_Size"].mean(), 2
            ),
        }
