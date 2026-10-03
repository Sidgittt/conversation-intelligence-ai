from modules.rag.retriever import ConversationRetriever
from modules.agent.evidence_builder import EvidenceBuilder
from modules.agent.llm_agent import LLMConversationAgent


class ConversationAgent:

    def __init__(self, ai_df, messages_df=None):
        self.ai_df = ai_df
        self.messages_df = messages_df
        self.retriever = ConversationRetriever(
            ai_df,
            messages_df,
        )
        self.evidence_builder = EvidenceBuilder()
        self.llm_agent = LLMConversationAgent()

    def ask(self, question):
        results = self.retriever.retrieve(
            question,
            top_k=5,
        )

        if results.empty:
            return {
                "answer": "No relevant conversations were found for this question.",
                "evidence": results,
                "evidence_count": 0,
            }

        evidence = self.evidence_builder.build(results)
        answer = self.llm_agent.ask(
            question,
            evidence,
        )

        return {
            "answer": answer,
            "evidence": results,
            "evidence_count": len(results),
        }
