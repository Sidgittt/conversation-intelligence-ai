import pandas as pd
from pathlib import Path


class ResultManager:

    def __init__(self):

        self.output_file = (
            Path("output") /
            "ai_analysis.csv"
        )

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    # ========================================================
    # CHECK WHETHER CONVERSATION WAS ALREADY ANALYZED
    # ========================================================

    def already_processed(
        self,
        conversation_id
    ):

        if not self.output_file.exists():

            return False

        try:

            df = pd.read_csv(
                self.output_file
            )

        except Exception:

            return False

        if (
            df.empty
            or "Conversation_ID"
            not in df.columns
        ):

            return False

        return str(
            conversation_id
        ) in (
            df["Conversation_ID"]
            .astype(str)
            .values
        )

    # ========================================================
    # SAVE AI RESULT
    # ========================================================

    def save(
        self,
        conversation_id,
        result
    ):

        relationship = result.get(
            "relationship",
            {}
        )

        context_analysis = result.get(
            "context_specific_analysis",
            {}
        )

        romantic = context_analysis.get(
            "romantic",
            {}
        )

        friendship = context_analysis.get(
            "friendship",
            {}
        )

        professional = context_analysis.get(
            "professional",
            {}
        )

        personal_growth = context_analysis.get(
            "personal_growth",
            {}
        )

        universal = result.get(
            "universal_analysis",
            {}
        )

        toxicity = result.get(
            "toxicity",
            {}
        )

        flags = result.get(
            "conversation_flags",
            {}
        )

        quality = result.get(
            "conversation_quality",
            {}
        )

        # ====================================================
        # BUILD RESULT ROW
        # ====================================================

        row = {

            "Conversation_ID":
                conversation_id,

            "Summary":
                result.get(
                    "summary",
                    ""
                ),

            "Conversation_Type":
                result.get(
                    "conversation_type",
                    ""
                ),

            "Conversation_Sufficiency":
                result.get(
                    "conversation_sufficiency",
                    "unknown"
                ),

            "Sufficiency_Reason":
                result.get(
                    "sufficiency_reason",
                    ""
                ),

            "Primary_Context":
                result.get(
                    "primary_context",
                    "unknown"
                ),

            "Secondary_Contexts":
                ", ".join(
                    result.get(
                        "secondary_contexts",
                        []
                    )
                ),

            "Context_Confidence":
                result.get(
                    "context_confidence",
                    0
                ),

            "Primary_Emotion":
                result.get(
                    "primary_emotion",
                    "unknown"
                ),

            "Secondary_Emotion":
                result.get(
                    "secondary_emotion",
                    "unknown"
                ),

            "Emotion_Scores":
                str(
                    result.get(
                        "emotion_scores",
                        {}
                    )
                ),

            "Topics":
                ", ".join(
                    result.get(
                        "topics",
                        []
                    )
                ),

            "Languages":
                ", ".join(
                    result.get(
                        "languages_detected",
                        []
                    )
                ),

            # ------------------------------------------------
            # Relationship
            # ------------------------------------------------

            "Relationship_Stage":
                relationship.get(
                    "stage"
                ),

            "Trust_Score":
                relationship.get(
                    "trust_score"
                ),

            "Communication_Score":
                relationship.get(
                    "communication_score"
                ),

            "Care_Score":
                relationship.get(
                    "care_score"
                ),

            "Respect_Score":
                relationship.get(
                    "respect_score"
                ),

            "Romance_Score":
                relationship.get(
                    "romance_score"
                ),

            "Friendship_Score":
                relationship.get(
                    "friendship_score"
                ),

            "Overall_Relationship_Score":
                relationship.get(
                    "overall_relationship_score"
                ),

            # ------------------------------------------------
            # Context-Specific Analysis
            # ------------------------------------------------

            "Romance_Context_Score":
                romantic.get(
                    "romance_score"
                ),

            "Emotional_Connection_Score":
                romantic.get(
                    "emotional_connection_score"
                ),

            "Friendship_Strength_Score":
                friendship.get(
                    "friendship_strength_score"
                ),

            "Friendship_Support_Score":
                friendship.get(
                    "support_score"
                ),

            "Professionalism_Score":
                professional.get(
                    "professionalism_score"
                ),

            "Collaboration_Score":
                professional.get(
                    "collaboration_score"
                ),

            "Responsiveness_Score":
                professional.get(
                    "responsiveness_score"
                ),

            "Goal_Orientation_Score":
                personal_growth.get(
                    "goal_orientation_score"
                ),

            "Personal_Growth_Support_Score":
                personal_growth.get(
                    "support_score"
                ),

            # ------------------------------------------------
            # Universal Analysis
            # ------------------------------------------------

            "Communication_Score":
                universal.get(
                    "communication_score"
                ),

            "Engagement_Score":
                universal.get(
                    "engagement_score"
                ),

            "Positivity_Score":
                universal.get(
                    "positivity_score"
                ),

            "Emotional_Depth_Score":
                universal.get(
                    "emotional_depth_score"
                ),

            "Clarity_Score":
                universal.get(
                    "clarity_score"
                ),

            "Conflict_Score":
                universal.get(
                    "conflict_score"
                ),

            "Support_Score":
                universal.get(
                    "support_score"
                ),

            "Overall_Conversation_Score":
                universal.get(
                    "overall_conversation_score"
                ),

            # ------------------------------------------------
            # Toxicity
            # ------------------------------------------------

            "Toxicity_Level":
                toxicity.get(
                    "level"
                ),

            "Toxicity_Score":
                toxicity.get(
                    "score"
                ),

            "Bad_Words":
                ", ".join(
                    toxicity.get(
                        "bad_words",
                        []
                    )
                ),

            "Personal_Attacks":
                toxicity.get(
                    "personal_attacks"
                ),

            "Blaming":
                toxicity.get(
                    "blaming"
                ),

            "Gaslighting":
                toxicity.get(
                    "gaslighting"
                ),

            "Manipulation":
                toxicity.get(
                    "manipulation"
                ),

            # ------------------------------------------------
            # Conversation Flags
            # ------------------------------------------------

            "Argument":
                flags.get(
                    "argument"
                ),

            "Apology":
                flags.get(
                    "apology"
                ),

            "Future_Planning":
                flags.get(
                    "future_planning"
                ),

            "Family_Discussion":
                flags.get(
                    "family_discussion"
                ),

            "Marriage_Discussion":
                flags.get(
                    "marriage_discussion"
                ),

            "Financial_Discussion":
                flags.get(
                    "financial_discussion"
                ),

            "Career_Discussion":
                flags.get(
                    "career_discussion"
                ),

            "Late_Reply_After_Serious_Chat":
                flags.get(
                    "late_reply_after_serious_chat"
                ),

            "Ghosting":
                flags.get(
                    "ghosting"
                ),

            "Double_Texting":
                flags.get(
                    "double_texting"
                ),

            "Silent_Treatment":
                flags.get(
                    "silent_treatment"
                ),

            "Sexting":
                flags.get(
                    "sexting"
                ),

            "Meeting_Planned":
                flags.get(
                    "meeting_planned"
                ),

            "Compliment":
                flags.get(
                    "compliment"
                ),

            "Support_During_Difficult_Time":
                flags.get(
                    "support_during_difficult_time"
                ),

            # ------------------------------------------------
            # Quality
            # ------------------------------------------------

            "Conversation_Quality_Score":
                quality.get(
                    "overall_score"
                ),

            "Quality_Engagement_Score":
                quality.get(
                    "engagement_score"
                ),

            "Quality_Positivity_Score":
                quality.get(
                    "positivity_score"
                ),

            "Quality_Emotional_Depth_Score":
                quality.get(
                    "emotional_depth_score"
                ),

            "Quality_Clarity_Score":
                quality.get(
                    "clarity_score"
                ),

            # ------------------------------------------------
            # Confidence
            # ------------------------------------------------

            "Confidence":
                result.get(
                    "confidence",
                    0
                )
        }

        new_df = pd.DataFrame(
            [row]
        )

        # ====================================================
        # UPDATE EXISTING DATASET
        # ====================================================

        if self.output_file.exists():

            try:

                old_df = pd.read_csv(
                    self.output_file
                )

            except Exception:

                old_df = pd.DataFrame()

            if (
                not old_df.empty
                and "Conversation_ID"
                in old_df.columns
            ):

                old_df = old_df[
                    old_df[
                        "Conversation_ID"
                    ].astype(str)
                    != str(conversation_id)
                ]

                new_df = pd.concat(
                    [
                        old_df,
                        new_df
                    ],
                    ignore_index=True
                )

        # ====================================================
        # SORT
        # ====================================================

        if "Conversation_ID" in new_df.columns:

            new_df = new_df.sort_values(
                "Conversation_ID"
            )

        # ====================================================
        # SAVE
        # ====================================================

        new_df.to_csv(
            self.output_file,
            index=False,
            encoding="utf-8-sig"
        )