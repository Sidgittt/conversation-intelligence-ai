from pathlib import Path

import pandas as pd


class ConversationRetriever:

    TEMPORAL_WORDS = {
        "over time", "across time", "over the years", "across the years",
        "history", "historical", "changed", "change", "evolved", "evolution",
        "trend", "trends", "progression", "before", "after", "earlier",
        "later", "recent", "recently", "past", "year", "years", "month",
        "months", "timeline", "when did",
    }

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "what", "how", "has", "have",
        "had", "did", "does", "do", "our", "my", "your", "their", "is",
        "are", "was", "were", "in", "on", "to", "of", "for", "with", "from",
        "across", "over", "me", "we", "i", "it", "this", "that", "these",
        "those", "between", "during", "there", "any", "more", "show", "tell",
        "can", "could", "would", "please",
    }

    SEARCH_COLUMNS = [
        "Summary", "Primary_Context", "Secondary_Contexts",
        "Primary_Emotion", "Secondary_Emotion", "Topics",
        "Conversation_Type", "Relationship_Stage", "Green_Flags",
        "Red_Flags", "Important_Moments", "Toxicity_Level",
        "Toxicity_Explanation",
    ]

    def __init__(self, ai_df, messages_df=None, conversation_index_path=None):
        self.ai_df = ai_df.copy()
        self.messages_df = (
            messages_df.copy()
            if messages_df is not None
            else pd.DataFrame()
        )

        if conversation_index_path is None:
            conversation_index_path = Path("output") / "conversation_index.csv"

        self.conversation_index = pd.DataFrame()

        if Path(conversation_index_path).exists():
            try:
                self.conversation_index = pd.read_csv(conversation_index_path)
            except Exception:
                pass

        self._attach_timeline_data()
        self._prepare_messages()

    @staticmethod
    def _find_column(dataframe, candidates):
        for column in candidates:
            if column in dataframe.columns:
                return column
        return None

    def _attach_timeline_data(self):
        if self.ai_df.empty or "Conversation_ID" not in self.ai_df.columns:
            return
        if self.conversation_index.empty:
            return
        if "Conversation_ID" not in self.conversation_index.columns:
            return

        timeline_columns = [
            column for column in [
                "Conversation_ID", "Start_Time", "End_Time",
                "Message_Count", "Duration_Minutes", "Participants",
            ]
            if column in self.conversation_index.columns
        ]

        timeline = self.conversation_index[timeline_columns].copy()
        self.ai_df["Conversation_ID"] = self.ai_df["Conversation_ID"].astype(str)
        timeline["Conversation_ID"] = timeline["Conversation_ID"].astype(str)

        self.ai_df = self.ai_df.merge(
            timeline,
            on="Conversation_ID",
            how="left",
            suffixes=("", "_timeline"),
        )

    def _prepare_messages(self):
        if self.messages_df.empty:
            return

        conversation_column = self._find_column(
            self.messages_df,
            ["Conversation_ID", "conversation_id", "Conversation", "conversation"],
        )
        message_column = self._find_column(
            self.messages_df,
            ["Message", "message", "Text", "text", "Content", "content"],
        )
        datetime_column = self._find_column(
            self.messages_df,
            ["Datetime", "DateTime", "Timestamp", "timestamp", "Date"],
        )
        sender_column = self._find_column(
            self.messages_df,
            ["Sender", "sender", "Author", "author"],
        )

        if conversation_column is None or message_column is None:
            self.messages_df = pd.DataFrame()
            return

        self.messages_df = self.messages_df.copy()
        self.messages_df["_Conversation_ID"] = (
            self.messages_df[conversation_column].astype(str)
        )
        self.messages_df["_Message_Text"] = (
            self.messages_df[message_column].fillna("").astype(str)
        )
        self.messages_df["_Datetime"] = (
            pd.to_datetime(
                self.messages_df[datetime_column],
                errors="coerce",
            )
            if datetime_column
            else pd.Series(pd.NaT, index=self.messages_df.index)
        )
        self.messages_df["_Sender"] = (
            self.messages_df[sender_column].fillna("").astype(str)
            if sender_column
            else ""
        )

    def _is_temporal_query(self, query):
        query = query.lower()
        return any(phrase in query for phrase in self.TEMPORAL_WORDS)

    def _query_terms(self, query):
        raw_terms = [
            word.strip(".,!?;:()[]{}")
            for word in query.lower().split()
        ]
        return [
            word for word in raw_terms
            if len(word) > 2 and word not in self.STOP_WORDS
        ]

    def _score_text(self, text, terms):
        text = str(text).lower()
        return sum(1 for term in terms if term in text)

    def _analysis_candidates(self, terms):
        if self.ai_df.empty:
            return pd.DataFrame()

        result = self.ai_df.copy()
        result["Search_Score"] = [
            self._score_text(
                " ".join(
                    str(row.get(column, ""))
                    for column in self.SEARCH_COLUMNS
                    if column in row.index
                ),
                terms,
            )
            for _, row in result.iterrows()
        ]
        result = result[result["Search_Score"] > 0].copy()
        if not result.empty:
            result["Evidence_Source"] = "analysis"
        return result

    def _message_candidates(self, terms):
        if self.messages_df.empty:
            return pd.DataFrame()

        result = self.messages_df.copy()
        result["Message_Search_Score"] = [
            self._score_text(text, terms)
            for text in result["_Message_Text"]
        ]
        return result[result["Message_Search_Score"] > 0].copy()

    def _merge_message_evidence(self, analysis_candidates, message_hits):
        if message_hits.empty:
            return analysis_candidates

        message_scores = (
            message_hits.groupby("_Conversation_ID")["Message_Search_Score"]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "_Conversation_ID": "Conversation_ID",
                    "Message_Search_Score": "Message_Evidence_Score",
                }
            )
        )

        message_counts = (
            message_hits.groupby("_Conversation_ID")
            .size()
            .reset_index(name="Matching_Message_Count")
            .rename(columns={"_Conversation_ID": "Conversation_ID"})
        )

        message_summary = message_scores.merge(
            message_counts,
            on="Conversation_ID",
            how="left",
        )
        message_summary["Conversation_ID"] = (
            message_summary["Conversation_ID"].astype(str)
        )

        if analysis_candidates.empty:
            result = self.ai_df.copy()
            result["Conversation_ID"] = result["Conversation_ID"].astype(str)
            result = result.merge(
                message_summary,
                on="Conversation_ID",
                how="inner",
            )
            result["Search_Score"] = 0
        else:
            result = analysis_candidates.copy()
            result["Conversation_ID"] = result["Conversation_ID"].astype(str)
            result = result.merge(
                message_summary,
                on="Conversation_ID",
                how="outer",
            )

        result["Search_Score"] = pd.to_numeric(
            result.get("Search_Score", 0),
            errors="coerce",
        ).fillna(0)

        result["Message_Evidence_Score"] = pd.to_numeric(
            result.get("Message_Evidence_Score", 0),
            errors="coerce",
        ).fillna(0)

        result["Search_Score"] = (
            result["Search_Score"] +
            result["Message_Evidence_Score"]
        )

        def source(row):
            has_analysis = row.get("Search_Score", 0) > row.get(
                "Message_Evidence_Score", 0
            )
            has_messages = row.get("Message_Evidence_Score", 0) > 0
            if has_analysis and has_messages:
                return "analysis + raw messages"
            if has_messages:
                return "raw messages"
            return "analysis"

        result["Evidence_Source"] = result.apply(source, axis=1)
        return result

    def _temporal_diversity(self, result, max_results):
        if result.empty:
            return result.head(max_results)

        result = result.copy()

        if "Start_Time" not in result.columns:
            return result.sort_values(
                "Search_Score", ascending=False
            ).head(max_results)

        result["Start_Time"] = pd.to_datetime(
            result["Start_Time"], errors="coerce"
        )

        valid = result[result["Start_Time"].notna()].copy()
        invalid = result[result["Start_Time"].isna()].copy()

        if valid.empty:
            return result.sort_values(
                "Search_Score", ascending=False
            ).head(max_results)

        valid["Year"] = valid["Start_Time"].dt.year
        selected = []
        selected_ids = set()

        for year in sorted(valid["Year"].dropna().unique()):
            year_rows = valid[
                valid["Year"] == year
            ].sort_values(
                "Search_Score", ascending=False
            )
            if not year_rows.empty:
                row = year_rows.iloc[0]
                selected.append(row)
                selected_ids.add(row.name)

        remaining = valid[
            ~valid.index.isin(selected_ids)
        ].sort_values(
            "Search_Score", ascending=False
        )

        for _, row in remaining.iterrows():
            if len(selected) >= max_results:
                break
            selected.append(row)

        for _, row in invalid.iterrows():
            if len(selected) >= max_results:
                break
            selected.append(row)

        return pd.DataFrame(selected).head(max_results)

    def retrieve(self, query, top_k=10):
        query = str(query).strip().lower()
        if not query:
            return pd.DataFrame()

        terms = self._query_terms(query)
        if not terms:
            return pd.DataFrame()

        analysis_candidates = self._analysis_candidates(terms)
        message_hits = self._message_candidates(terms)

        result = self._merge_message_evidence(
            analysis_candidates,
            message_hits,
        )

        if result.empty:
            return result

        result["Search_Score"] = pd.to_numeric(
            result["Search_Score"], errors="coerce"
        ).fillna(0)
        result = result[result["Search_Score"] > 0].copy()

        if result.empty:
            return result

        if self._is_temporal_query(query):
            return self._temporal_diversity(
                result,
                max(top_k, 20),
            )

        return result.sort_values(
            "Search_Score",
            ascending=False,
        ).head(top_k)
