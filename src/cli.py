"""Command-line interface for the movie RAG app."""
from src.neo4j_client import Neo4jClient
from src.rag_engine import ask
from src.llm_client import check_ollama_alive


def main():
    print("=== Neo4j Movie RAG (CLI) ===")
    if not check_ollama_alive():
        print("WARNING: Could not reach Ollama at the configured OLLAMA_HOST."
              " Make sure `ollama serve` is running.")

    client = Neo4jClient()
    try:
        client.verify_connectivity()
        print("Connected to Neo4j.\n")
    except Exception as e:  # noqa: BLE001
        print(f"Could not connect to Neo4j: {e}")
        return

    print("Ask a question about the movie graph (e.g. 'Who directed The Matrix?').")
    print("Type 'schema' to see the graph schema, or 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break
        if question.lower() == "schema":
            print(client.get_schema_text())
            continue

        result = ask(client, question)
        print(f"\n[Cypher]  {result.cypher}")
        if result.error:
            print(f"[Error]   {result.error}\n")
            continue
        print(f"[Rows]    {result.rows}")
        print(f"[Answer]  {result.answer}\n")

    client.close()


if __name__ == "__main__":
    main()
