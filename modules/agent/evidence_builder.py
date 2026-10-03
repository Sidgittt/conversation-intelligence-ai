class EvidenceBuilder:

    def build(self, retrieved_df):
        evidence = []

        for _, row in retrieved_df.iterrows():
            evidence.append(
                {
                    "Conversation_ID": row.get("Conversation_ID"),
                    "Start_Time": row.get("Start_Time"),
                    "End_Time": row.get("End_Time"),
                    "Message_Count": row.get("Message_Count"),
                    "Matching_Message_Count": row.get("Matching_Message_Count"),
                    "Evidence_Source": row.get("Evidence_Source"),
                    "Summary": row.get("Summary"),
                    "Primary_Context": row.get("Primary_Context"),
                    "Secondary_Contexts": row.get("Secondary_Contexts"),
                    "Conversation_Type": row.get("Conversation_Type"),
                    "Primary_Emotion": row.get("Primary_Emotion"),
                    "Secondary_Emotion": row.get("Secondary_Emotion"),
                    "Topics": row.get("Topics"),
                    "Relationship_Stage": row.get("Relationship_Stage"),
                    "Trust": row.get("Trust_Score"),
                    "Communication": row.get("Communication_Score"),
                    "Care": row.get("Care_Score"),
                    "Respect": row.get("Respect_Score"),
                    "Romance": row.get("Romance_Score"),
                    "Friendship": row.get("Friendship_Score"),
                    "Conflict": row.get("Conflict_Score"),
                    "Support": row.get("Support_Score"),
                    "Green_Flags": row.get("Green_Flags"),
                    "Red_Flags": row.get("Red_Flags"),
                    "Important_Moments": row.get("Important_Moments"),
                    "Toxicity_Level": row.get("Toxicity_Level"),
                    "Toxicity_Explanation": row.get("Toxicity_Explanation"),
                    "Conversation_Sufficiency": row.get("Conversation_Sufficiency"),
                    "Confidence": row.get("Confidence"),
                }
            )

        return evidence
