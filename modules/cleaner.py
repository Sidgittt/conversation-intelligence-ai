
"""
cleaner.py
Data cleaning module for WhatsApp Analytics
"""

from __future__ import annotations

import re
import pandas as pd


class ChatCleaner:
    """Cleans parsed WhatsApp dataframe."""

    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

    MEDIA_PATTERNS = (
        "<Media omitted>",
        "image omitted",
        "video omitted",
        "audio omitted",
        "document omitted",
        "GIF omitted",
        "sticker omitted",
    )

    DELETED_PATTERNS = (
        "This message was deleted",
        "You deleted this message",
    )

    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F300-\U0001FAFF"
        "\U00002600-\U000026FF"
        "\U00002700-\U000027BF"
        "]",
        flags=re.UNICODE,
    )

    GREETING_WORDS = {
        "hi", "hello", "hey", "hii", "hiii",
        "good morning", "good night", "good evening",
        "namaste", "namaskar"
    }

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def clean(self) -> pd.DataFrame:

        self.df["Message"] = (
            self.df["Message"]
            .fillna("")
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        self.df["Character_Count"] = self.df["Message"].str.len()

        self.df["Word_Count"] = (
            self.df["Message"]
            .str.split()
            .apply(len)
        )

        self.df["URL_Count"] = self.df["Message"].apply(
            lambda x: len(self.URL_PATTERN.findall(x))
        )

        self.df["Emoji_Count"] = self.df["Message"].apply(
            lambda x: len(self.EMOJI_PATTERN.findall(x))
        )

        self.df["Is_Deleted"] = self.df["Message"].apply(
            lambda x: any(p.lower() in x.lower() for p in self.DELETED_PATTERNS)
        )

        self.df["Is_Media"] = self.df["Message"].apply(
            lambda x: any(p.lower() in x.lower() for p in self.MEDIA_PATTERNS)
        )

        self.df["Is_Question"] = self.df["Message"].str.endswith("?")

        self.df["Is_Empty"] = self.df["Message"].eq("")

        self.df["Is_Greeting"] = self.df["Message"].str.lower().apply(
            lambda x: any(x.startswith(word) for word in self.GREETING_WORDS)
        )

        return self.df
