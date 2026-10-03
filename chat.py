import pandas as pd

from modules.agent.llm_agent import LLMConversationAgent


def main():

    df = pd.read_csv("output/ai_analysis.csv")

    agent = LLMConversationAgent(df)

    print("=" * 70)
    print("WhatsApp AI Assistant")
    print("=" * 70)

    while True:

        question = input("\nYou : ")

        if question.lower() == "exit":
            break

        print("\nThinking...\n")

        answer = agent.ask(question)

        print(answer)


if __name__ == "__main__":
    main()