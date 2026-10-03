from langdetect import detect


class LanguageDetector:

    def detect(self, text):

        try:
            return detect(text)

        except:
            return "unknown"