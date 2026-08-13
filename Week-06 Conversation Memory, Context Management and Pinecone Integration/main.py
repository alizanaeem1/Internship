from config import DATA_FOLDER
from ingest import index_folder
from watcher import start_watcher
from query import ask_question


def main():
    """
    Main entry point for the QHSE and DOT Compliance RAG System.
    """

    # Index all documents
    # index_folder(DATA_FOLDER, force=True)

    # Start real-time watcher
    observer = start_watcher()

    print("\n======================================")
    print("   QHSE & DOT Compliance RAG Ready")
    print("Type 'exit' to quit.")
    print("======================================")

    try:
        while True:
            question = input("\n>>> ").strip()

            if question.lower() == "exit":
                print("\nClosing QHSE & DOT Compliance RAG System...")
                break

            if not question:
                print(
                    "Please enter a QHSE or DOT Compliance-related question."
                )
                continue

            answer = ask_question(question)

            print("\nAnswer:\n")
            print(answer)

    except KeyboardInterrupt:
        print("\nStopping system...")

    finally:
        observer.stop()
        observer.join()
        print("Watcher Stopped.")
        print("Goodbye!")


if __name__ == "__main__":
    main()