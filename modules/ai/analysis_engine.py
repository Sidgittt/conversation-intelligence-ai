from pathlib import Path
import json

from modules.ai.result_manager import ResultManager
from modules.parser import WhatsAppParser
from modules.cleaner import ChatCleaner
from modules.conversation import ConversationEngine
from modules.ai.analyzers.conversation_analyzer import ConversationAnalyzer


class AnalysisEngine:

    def __init__(self, chat_file="data/uploaded_conversation.txt"):

        self.chat_file = chat_file

        self.output_folder = Path("output")
        self.output_folder.mkdir(exist_ok=True)

        self.prepared_messages_file = (
            self.output_folder / "prepared_messages.csv"
        )

        self.conversation_index_file = (
            self.output_folder / "conversation_index.csv"
        )

        self.chat_profile_file = (
            self.output_folder / "chat_profile.json"
        )

    # =========================================================
    # LOCAL PREPARATION
    # =========================================================

    def prepare(self):

        if not Path(self.chat_file).exists():
            raise FileNotFoundError(
                f"Conversation file not found: {self.chat_file}"
            )

        # 1. Parse
        parser = WhatsAppParser(self.chat_file)
        df = parser.parse_messages()

        if df.empty:
            raise ValueError("No messages found in conversation.")

        # 2. Clean
        cleaner = ChatCleaner(df)
        df = cleaner.clean()

        if df.empty:
            raise ValueError("No messages remain after cleaning.")

        # 3. Build conversations
        conversation_engine = ConversationEngine(df)
        conversations = conversation_engine.build()

        if conversations.empty:
            raise ValueError("No conversations could be built.")

        # 4. Save prepared messages
        conversations.to_csv(
            self.prepared_messages_file,
            index=False,
            encoding="utf-8-sig"
        )

        # 5. Build conversation index
        conversation_index = (
            conversations
            .groupby("Conversation_ID")
            .agg(
                Start_Time=("Datetime", "min"),
                End_Time=("Datetime", "max"),
                Message_Count=("Message_ID", "count"),
                Participants=(
                    "Sender",
                    lambda x: ", ".join(
                        sorted(
                            x.dropna()
                            .astype(str)
                            .unique()
                            .tolist()
                        )
                    )
                ),
                Started_By=("Started_By", "first"),
                Ended_By=("Ended_By", "first"),
                Character_Count=("Character_Count", "sum"),
                Word_Count=("Word_Count", "sum"),
                Question_Count=("Is_Question", "sum"),
                Emoji_Count=("Emoji_Count", "sum")
            )
            .reset_index()
        )

        # 6. Calculate duration
        conversation_index["Duration_Minutes"] = (
            conversation_index["End_Time"]
            - conversation_index["Start_Time"]
        ).dt.total_seconds() / 60

        conversation_index["Duration_Minutes"] = (
            conversation_index["Duration_Minutes"].round(1)
        )

        # 7. Save conversation index
        conversation_index.to_csv(
            self.conversation_index_file,
            index=False,
            encoding="utf-8-sig"
        )

        # 8. Create chat profile
        participants = (
            conversations["Sender"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        sender_counts = (
            conversations["Sender"]
            .value_counts()
            .to_dict()
        )

        profile = {
            "chat_file": str(self.chat_file),
            "total_messages": int(len(conversations)),
            "total_conversations": int(
                conversations["Conversation_ID"].nunique()
            ),
            "participants": participants,
            "messages_by_participant": {
                str(key): int(value)
                for key, value in sender_counts.items()
            },
            "start_date": str(
                conversations["Datetime"].min()
            ),
            "end_date": str(
                conversations["Datetime"].max()
            ),
            "average_messages_per_conversation": round(
                conversations["Conversation_Size"].mean(),
                2
            ),
            "largest_conversation": int(
                conversations["Conversation_Size"].max()
            )
        }

        with open(
            self.chat_profile_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                profile,
                file,
                indent=4
            )

        return {
            "messages": conversations,
            "conversations": conversation_index,
            "profile": profile
        }

    # =========================================================
    # AI ANALYSIS
    # =========================================================

    def run(self, limit=5, force_reanalysis=False):

        prepared = self.prepare()

        conversations = prepared["messages"]

        analyzer = ConversationAnalyzer()
        result_manager = ResultManager()

        conversation_ids = (
            conversations["Conversation_ID"]
            .unique()
        )

        if limit is not None:
            conversation_ids = conversation_ids[:limit]

        success = 0
        failed = 0
        skipped = 0

        for conversation_id in conversation_ids:

            if (
                not force_reanalysis
                and result_manager.already_processed(
                    conversation_id
                )
            ):
                skipped += 1
                continue

            conversation_df = conversations[
                conversations["Conversation_ID"] == conversation_id
            ]

            conversation_text = "\n".join(
                f"{row['Sender']}: {row['Message']}"
                for _, row in conversation_df.iterrows()
            )

            try:

                result = analyzer.analyze(
                    conversation_text
                )

                result_manager.save(
                    conversation_id,
                    result
                )

                success += 1

            except Exception as error:

                print(
                    f"Error analyzing "
                    f"{conversation_id}: {error}"
                )

                failed += 1

        return {
            "messages": len(conversations),
            "conversations": int(
                conversations["Conversation_ID"].nunique()
            ),
            "successful": success,
            "failed": failed,
            "skipped": skipped,
            "profile": prepared["profile"]
        }