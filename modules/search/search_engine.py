import pandas as pd


class SearchEngine:

    def __init__(self, df):
        self.df = df

    def search_emotion(self, emotion):

        return self.df[
            self.df["Primary_Emotion"]
            .str.lower()
            == emotion.lower()
        ]

    def search_topic(self, topic):

        return self.df[
            self.df["Topics"]
            .str.contains(
                topic,
                case=False,
                na=False
            )
        ]

    def search_relationship_stage(self, stage):

        return self.df[
            self.df["Relationship_Stage"]
            .str.lower()
            == stage.lower()
        ]

    def search_trust(self, minimum_score):

        return self.df[
            self.df["Trust_Score"] >= minimum_score
        ]

    def search_romance(self, minimum_score):

        return self.df[
            self.df["Romance_Score"] >= minimum_score
        ]

    def search_toxicity(self, maximum_score):

        return self.df[
            self.df["Toxicity_Score"] <= maximum_score
        ]