import pandas as pd


class RelationshipReport:

    def __init__(self, df):

        self.df = df

    def generate(self):

        report = {}

        report["Total Conversations"] = len(self.df)

        report["Average Trust"] = round(
            self.df["Trust_Score"].mean(),
            2
        )

        report["Average Communication"] = round(
            self.df["Communication_Score"].mean(),
            2
        )

        report["Average Care"] = round(
            self.df["Care_Score"].mean(),
            2
        )

        report["Average Respect"] = round(
            self.df["Respect_Score"].mean(),
            2
        )

        report["Average Romance"] = round(
            self.df["Romance_Score"].mean(),
            2
        )

        report["Relationship Score"] = round(

            (
                self.df["Trust_Score"].mean()
                + self.df["Communication_Score"].mean()
                + self.df["Care_Score"].mean()
                + self.df["Respect_Score"].mean()
                + self.df["Romance_Score"].mean()

            ) / 5,

            2

        )

        report["Primary Emotion"] = (
            self.df["Primary_Emotion"]
            .mode()[0]
        )

        report["Conversation Type"] = (
            self.df["Conversation_Type"]
            .mode()[0]
        )

        report["Arguments"] = int(
            self.df["Argument"].sum()
        )

        report["Ghosting"] = int(
            self.df["Ghosting"].sum()
        )

        report["Average Toxicity"] = round(
            self.df["Toxicity_Score"].mean(),
            2
        )

        return report
    