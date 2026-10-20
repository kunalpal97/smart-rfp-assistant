
from app.services.rag import answer_rfp_question


QUESTION = (
    "What are the P1 and P2 response "
    "and resolution times?"
)


def main():
    for mode in ("semantic", "bm25", "hybrid"):
        print("\n" + "=" * 70)
        print("RETRIEVAL MODE:", mode.upper())

        try:
            result = answer_rfp_question(
                question=QUESTION,
                retrieval_mode=mode,
            )

            print("\nANSWER:")
            print(result["answer"])

            print("\nCITED SOURCES:")
            for source in result["sources"]:
                print(
                    f"- {source['source_id']}: "
                    f"{source['source_file']}"
                )
                print(f"  Chunk: {source['chunk_id']}")

            if not result["sources"]:
                print("No cited sources.")

        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
