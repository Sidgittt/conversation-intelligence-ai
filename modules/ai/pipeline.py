import json
import re

from openai import OpenAI

from .config import OPENAI_API_KEY
from .prompts import SYSTEM_PROMPT


class AIPipeline:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        self.model = "gpt-5-mini"

        self.max_output_tokens = 5000

    # ========================================================
    # MAIN ANALYSIS FUNCTION
    # ========================================================

    def analyze(self, conversation):

        if not conversation or not str(conversation).strip():

            return self._insufficient_result(
                "The conversation is empty."
            )

        conversation = str(conversation).strip()

        # ----------------------------------------------------
        # LOCAL SUFFICIENCY CHECK
        # ----------------------------------------------------

        sufficiency_result = (
            self._check_conversation_sufficiency(
                conversation
            )
        )

        if sufficiency_result is not None:

            return sufficiency_result

        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        try:

            response = self.client.responses.create(

                model=self.model,

                input=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": conversation
                    }
                ],

                max_output_tokens=self.max_output_tokens,

                text={
                    "format": {
                        "type": "json_object"
                    }
                },

                store=False
            )

            text = response.output_text

            if not text or not text.strip():

                return self._error_result(
                    "AI returned an empty response."
                )

            result = json.loads(text)

            if not isinstance(result, dict):

                return self._error_result(
                    "AI returned an invalid JSON object."
                )

            result = self._normalise_result(
                result
            )

            result = self._apply_sufficiency_rules(
                result
            )

            return result

        except json.JSONDecodeError:

            return self._error_result(
                "Invalid JSON returned by AI."
            )

        except Exception as error:

            print(
                f"AI Error: {error}"
            )

            return self._error_result(
                "AI Analysis Failed."
            )

    # ========================================================
    # LOCAL SUFFICIENCY CHECK
    # ========================================================

    def _check_conversation_sufficiency(
        self,
        conversation
    ):

        lines = [
            line.strip()
            for line in conversation.splitlines()
            if line.strip()
        ]

        meaningful_lines = []

        for line in lines:

            message = self._extract_message_text(
                line
            )

            if not message:
                continue

            meaningful_text = re.sub(
                r"[\W_]+",
                "",
                message,
                flags=re.UNICODE
            )

            if meaningful_text:

                meaningful_lines.append(
                    message
                )

        message_count = len(
            meaningful_lines
        )

        total_text = " ".join(
            meaningful_lines
        )

        text_without_emojis = re.sub(
            r"[^\w\s]",
            "",
            total_text,
            flags=re.UNICODE
        ).strip()

        character_count = len(
            text_without_emojis
        )

        # ----------------------------------------------------
        # VERY SHORT CONVERSATION
        # ----------------------------------------------------

        if message_count <= 2:

            return self._insufficient_result(
                "The conversation contains only "
                f"{message_count} meaningful message(s). "
                "There is not enough evidence to evaluate "
                "communication or relationship quality."
            )

        # ----------------------------------------------------
        # VERY LITTLE MEANINGFUL TEXT
        # ----------------------------------------------------

        if character_count < 30:

            return self._insufficient_result(
                "The conversation contains very little "
                "meaningful text. Relationship and quality "
                "scores cannot be evaluated reliably."
            )

        return None

    # ========================================================
    # EXTRACT MESSAGE TEXT
    # ========================================================

    def _extract_message_text(self, line):

        # Format:
        # Sender: Message

        if ":" in line:

            parts = line.split(
                ":",
                1
            )

            if len(parts) == 2:

                return parts[1].strip()

        return line.strip()

    # ========================================================
    # APPLY SUFFICIENCY RULES
    # ========================================================

    def _apply_sufficiency_rules(self, result):

        sufficiency = result.get(
            "conversation_sufficiency",
            "limited"
        )

        sufficiency = str(
            sufficiency
        ).strip().lower()

        if sufficiency not in {
            "sufficient",
            "limited",
            "insufficient"
        }:

            sufficiency = "limited"

        result[
            "conversation_sufficiency"
        ] = sufficiency

        # ----------------------------------------------------
        # INSUFFICIENT CONVERSATION
        # ----------------------------------------------------

        if sufficiency == "insufficient":

            self._set_all_scores_to_null(
                result
            )

            result[
                "confidence"
            ] = min(
                self._safe_number(
                    result.get(
                        "confidence",
                        0
                    )
                ),
                20
            )

        # ----------------------------------------------------
        # LIMITED CONVERSATION
        # ----------------------------------------------------

        elif sufficiency == "limited":

            result[
                "confidence"
            ] = min(
                self._safe_number(
                    result.get(
                        "confidence",
                        0
                    )
                ),
                50
            )

        return result

    # ========================================================
    # SET UNSUPPORTED SCORES TO NULL
    # ========================================================

    def _set_all_scores_to_null(self, result):

        relationship = result.get(
            "relationship",
            {}
        )

        for key in [
            "trust_score",
            "communication_score",
            "care_score",
            "respect_score",
            "romance_score",
            "friendship_score",
            "overall_relationship_score"
        ]:

            relationship[key] = None

        result[
            "relationship"
        ] = relationship

        universal = result.get(
            "universal_analysis",
            {}
        )

        for key in [
            "communication_score",
            "engagement_score",
            "positivity_score",
            "emotional_depth_score",
            "clarity_score",
            "conflict_score",
            "support_score",
            "overall_conversation_score"
        ]:

            universal[key] = None

        result[
            "universal_analysis"
        ] = universal

        context_analysis = result.get(
            "context_specific_analysis",
            {}
        )

        for context_name in context_analysis:

            context_data = context_analysis[
                context_name
            ]

            if not isinstance(
                context_data,
                dict
            ):
                continue

            for key in context_data:

                if key.endswith(
                    "_score"
                ):

                    context_data[key] = None

        result[
            "context_specific_analysis"
        ] = context_analysis

        quality = result.get(
            "conversation_quality",
            {}
        )

        for key in [
            "overall_score",
            "engagement_score",
            "positivity_score",
            "emotional_depth_score",
            "clarity_score"
        ]:

            quality[key] = None

        result[
            "conversation_quality"
        ] = quality

        toxicity = result.get(
            "toxicity",
            {}
        )

        toxicity[
            "score"
        ] = None

        toxicity[
            "level"
        ] = "not_evaluable"

        result[
            "toxicity"
        ] = toxicity

        return result

    # ========================================================
    # NORMALISE RESULT
    # ========================================================

    def _normalise_result(self, result):

        default = self._error_result(
            "AI analysis completed."
        )

        return self._merge_dicts(
            default,
            result
        )

    # ========================================================
    # MERGE DICTIONARIES
    # ========================================================

    def _merge_dicts(self, default, actual):

        if not isinstance(
            default,
            dict
        ):

            return actual

        if not isinstance(
            actual,
            dict
        ):

            return default

        merged = default.copy()

        for key, value in actual.items():

            if (
                key in merged
                and isinstance(
                    merged[key],
                    dict
                )
                and isinstance(
                    value,
                    dict
                )
            ):

                merged[key] = self._merge_dicts(
                    merged[key],
                    value
                )

            else:

                merged[key] = value

        return merged

    # ========================================================
    # SAFE NUMBER
    # ========================================================

    def _safe_number(self, value):

        try:

            return int(
                float(value)
            )

        except Exception:

            return 0

    # ========================================================
    # INSUFFICIENT RESULT
    # ========================================================

    def _insufficient_result(self, reason):

        result = self._error_result(
            "Insufficient evidence."
        )

        result[
            "summary"
        ] = reason

        result[
            "conversation_sufficiency"
        ] = "insufficient"

        result[
            "sufficiency_reason"
        ] = reason

        result[
            "primary_context"
        ] = "unknown"

        result[
            "context_confidence"
        ] = 0

        result[
            "confidence"
        ] = 0

        self._set_all_scores_to_null(
            result
        )

        return result

    # ========================================================
    # ERROR RESULT
    # ========================================================

    def _error_result(self, message):

        return {

            "summary": message,

            "conversation_type": "",

            "conversation_sufficiency": "insufficient",

            "sufficiency_reason": message,

            "primary_context": "unknown",

            "secondary_contexts": [],

            "context_confidence": 0,

            "primary_emotion": "unknown",

            "secondary_emotion": "unknown",

            "emotion_scores": {},

            "topics": [],

            "languages_detected": [],

            "relationship": {

                "stage": None,

                "trust_score": None,

                "communication_score": None,

                "care_score": None,

                "respect_score": None,

                "romance_score": None,

                "friendship_score": None,

                "overall_relationship_score": None

            },

            "context_specific_analysis": {

                "romantic": {

                    "romance_score": None,

                    "emotional_connection_score": None

                },

                "friendship": {

                    "friendship_strength_score": None,

                    "support_score": None

                },

                "professional": {

                    "professionalism_score": None,

                    "collaboration_score": None,

                    "responsiveness_score": None

                },

                "personal_growth": {

                    "goal_orientation_score": None,

                    "support_score": None

                }

            },

            "universal_analysis": {

                "communication_score": None,

                "engagement_score": None,

                "positivity_score": None,

                "emotional_depth_score": None,

                "clarity_score": None,

                "conflict_score": None,

                "support_score": None,

                "overall_conversation_score": None

            },

            "toxicity": {

                "level": "not_evaluable",

                "score": None,

                "bad_words": [],

                "personal_attacks": False,

                "blaming": False,

                "gaslighting": False,

                "manipulation": False

            },

            "conversation_flags": {},

            "green_flags": [],

            "red_flags": [],

            "important_moments": [],

            "memorable_quotes": [],

            "conversation_quality": {

                "overall_score": None,

                "engagement_score": None,

                "positivity_score": None,

                "emotional_depth_score": None,

                "clarity_score": None

            },

            "confidence": 0

        }