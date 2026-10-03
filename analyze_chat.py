from modules.ai.analysis_engine import AnalysisEngine


def main():

    print("=" * 70)
    print("WHATSAPP AI ANALYZER")
    print("=" * 70)

    engine = AnalysisEngine(
        chat_file="data/WhatsApp Chat with XYZ.txt"
    )

    # Development mode:
    # Analyze only the first 5 conversations.
    # These will be re-analyzed using the latest AI prompt.
    result = engine.run(
        limit=None,
        force_reanalysis=True
    )

    print("\n" + "=" * 70)
    print("AI ANALYSIS SUMMARY")
    print("=" * 70)

    print(f"Messages       : {result['messages']}")
    print(f"Conversations  : {result['conversations']}")
    print(f"Successful     : {result['successful']}")
    print(f"Skipped        : {result['skipped']}")
    print(f"Failed         : {result['failed']}")

    print("=" * 70)


if __name__ == "__main__":
    main()