from config import DATA_FOLDER
from ingest import index_folder
from watcher import start_watcher
from query import ask_question


# First time force=True rakho
index_folder(DATA_FOLDER)
observer = start_watcher()

print("\nRAG System Ready")
print("Type 'exit' to quit.\n")

try:
    while True:
        question = input("\n>>> ")

        if question.lower() == "exit":
            break

        if not question.strip():
            print("Please provide a question.")
            continue

        answer = ask_question(question)
        
        print("\nAnswer:\n")
        print(answer)

except KeyboardInterrupt:
    print("\nStopping Watcher...")
    
finally:
    observer.stop()
    observer.join()
    print("Watcher Stopped.")