from modules.ai.analyzers.conversation_analyzer import ConversationAnalyzer


conversation = """
A: Hey! How are you?

B: I'm good 😊

A: Missing you a lot.

B: Me too ❤️

A: Let's meet this weekend.

B: Definitely! Can't wait.
"""


analyzer = ConversationAnalyzer()

result = analyzer.analyze(conversation)

print("\n========== AI RESULT ==========\n")

for key, value in result.items():
    print(f"{key}: {value}")