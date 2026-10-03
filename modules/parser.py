"""
parser.py - WhatsApp Chat Parser

Supports:

1. Old WhatsApp export format:
   7/9/26, 7:01 pm - Sender: Message

2. Old WhatsApp export format without AM/PM:
   7/9/26, 19:01 - Sender: Message

3. New WhatsApp export format:
   [7/9/26, 7:01:39 PM] Sender: Message

4. New WhatsApp export format without AM/PM:
   [7/9/26, 19:01:39] Sender: Message

5. Multi-line messages.
"""

from pathlib import Path
import re

import pandas as pd


class WhatsAppParser:

    def __init__(self, file_path):

        self.file_path = Path(file_path)

    # =========================================================
    # FILE HANDLING
    # =========================================================

    def file_exists(self):

        return self.file_path.exists()

    def load_chat(self):

        if not self.file_exists():

            raise FileNotFoundError(
                f"Chat file not found: {self.file_path}"
            )

        return self.file_path.read_text(
            encoding="utf-8-sig"
        ).splitlines()

    # =========================================================
    # MESSAGE DETECTION
    # =========================================================

    def extract_messages(self):
        """
        Separate the chat into individual messages.

        Supports both old and new WhatsApp date formats.
        """

        patterns = [

            # -------------------------------------------------
            # OLD FORMAT
            # Example:
            # 7/9/26, 7:01 pm - Sender: Message
            # -------------------------------------------------

            re.compile(
                r"^\d{1,2}/\d{1,2}/\d{2,4},\s*"
                r"\d{1,2}:\d{2}"
                r"(?:\s?[APMapm]{2})?"
                r"\s-\s"
            ),

            # -------------------------------------------------
            # NEW FORMAT
            # Example:
            # [7/9/26, 7:01:39 PM] Sender: Message
            # -------------------------------------------------

            re.compile(
                r"^\[\d{1,2}/\d{1,2}/\d{2,4},\s*"
                r"\d{1,2}:\d{2}"
                r"(?::\d{2})?"
                r"(?:\s?[APMapm]{2})?"
                r"\]\s"
            ),

        ]

        messages = []

        current_message = ""

        for line in self.load_chat():

            is_new_message = any(
                pattern.match(line)
                for pattern in patterns
            )

            if is_new_message:

                if current_message:

                    messages.append(current_message)

                current_message = line

            else:

                if current_message:

                    current_message += "\n" + line

        if current_message:

            messages.append(current_message)

        return messages

    # =========================================================
    # SINGLE MESSAGE PARSING
    # =========================================================

    def _parse_single(self, message):

        patterns = [

            # -------------------------------------------------
            # OLD FORMAT WITH AM/PM
            # Example:
            # 7/9/26, 7:01 PM - Sender: Message
            # -------------------------------------------------

            r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*"
            r"(\d{1,2}:\d{2}\s?[APMapm]{2})"
            r"\s-\s"
            r"([^:]+):\s?"
            r"(.*)$",

            # -------------------------------------------------
            # OLD FORMAT WITHOUT AM/PM
            # Example:
            # 7/9/26, 19:01 - Sender: Message
            # -------------------------------------------------

            r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*"
            r"(\d{1,2}:\d{2})"
            r"\s-\s"
            r"([^:]+):\s?"
            r"(.*)$",

            # -------------------------------------------------
            # NEW FORMAT WITH SECONDS AND AM/PM
            # Example:
            # [7/9/26, 7:01:39 PM] Sender: Message
            # -------------------------------------------------

            r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*"
            r"(\d{1,2}:\d{2}(?::\d{2})?\s?[APMapm]{2})"
            r"\]\s"
            r"([^:]+):\s?"
            r"(.*)$",

            # -------------------------------------------------
            # NEW FORMAT WITHOUT AM/PM
            # Example:
            # [7/9/26, 19:01:39] Sender: Message
            # -------------------------------------------------

            r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*"
            r"(\d{1,2}:\d{2}(?::\d{2})?)"
            r"\]\s"
            r"([^:]+):\s?"
            r"(.*)$",

        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                message,
                flags=re.DOTALL,
            )

            if match:

                return {
                    "Date": match.group(1),
                    "Time": match.group(2),
                    "Sender": match.group(3).strip(),
                    "Message": match.group(4)
                    .replace("\n", " ")
                    .strip(),
                }

        return None

    # =========================================================
    # COMPLETE PARSING
    # =========================================================

    def parse_messages(self):

        rows = []

        for message in self.extract_messages():

            row = self._parse_single(message)

            if row:

                rows.append(row)

        dataframe = pd.DataFrame(rows)

        if dataframe.empty:

            raise ValueError(
                "No messages parsed."
            )

        dataframe.insert(
            0,
            "Message_ID",
            range(1, len(dataframe) + 1),
        )

        dataframe.insert(
            1,
            "Datetime",
            pd.to_datetime(
                dataframe["Date"] + " " + dataframe["Time"],
                dayfirst=True,
                errors="coerce",
            ),
        )

        datetime_column = dataframe["Datetime"]

        dataframe["Year"] = datetime_column.dt.year
        dataframe["Month"] = datetime_column.dt.month
        dataframe["Month_Name"] = (
            datetime_column.dt.month_name()
        )
        dataframe["Day"] = datetime_column.dt.day
        dataframe["Day_Name"] = (
            datetime_column.dt.day_name()
        )
        dataframe["Hour"] = datetime_column.dt.hour
        dataframe["Minute"] = datetime_column.dt.minute

        return dataframe[
            [
                "Message_ID",
                "Datetime",
                "Date",
                "Time",
                "Year",
                "Month",
                "Month_Name",
                "Day",
                "Day_Name",
                "Hour",
                "Minute",
                "Sender",
                "Message",
            ]
        ]