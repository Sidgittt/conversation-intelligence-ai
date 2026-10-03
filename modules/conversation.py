
"""
conversation.py
Conversation engine
"""

import pandas as pd


class ConversationEngine:
    def __init__(self, df: pd.DataFrame, gap_minutes: int = 240):
        self.df = df.copy()
        self.gap_minutes = gap_minutes

    def build(self) -> pd.DataFrame:
        df = self.df.sort_values("Datetime").reset_index(drop=True)

        df["Gap_Minutes"] = (
            df["Datetime"]
            .diff()
            .dt.total_seconds()
            .div(60)
            .fillna(0)
        )

        df["Conversation_Start"] = (
            (df.index == 0) |
            (df["Gap_Minutes"] >= self.gap_minutes)
        )

        df["Conversation_ID"] = df["Conversation_Start"].cumsum()

        last_ids = (
            df.groupby("Conversation_ID")
              .tail(1)
              .index
        )

        df["Conversation_End"] = False
        df.loc[last_ids, "Conversation_End"] = True

        sizes = (
            df.groupby("Conversation_ID")
              .size()
              .rename("Conversation_Size")
        )

        df = df.merge(
            sizes,
            left_on="Conversation_ID",
            right_index=True,
            how="left"
        )

        starters = (
            df.groupby("Conversation_ID")["Sender"]
              .first()
              .rename("Started_By")
        )

        enders = (
            df.groupby("Conversation_ID")["Sender"]
              .last()
              .rename("Ended_By")
        )

        df = df.merge(
            starters,
            left_on="Conversation_ID",
            right_index=True,
            how="left"
        )

        df = df.merge(
            enders,
            left_on="Conversation_ID",
            right_index=True,
            how="left"
        )

        return df
