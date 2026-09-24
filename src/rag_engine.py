from src.nl2cypher import question_to_cypher
from src.neo4j_client import Neo4jClient
from src.llm_client import ollama_generate


ANSWER_SYSTEM_PROMPT = """
You are MovieRAG, a movie question-answering assistant.

Answer ONLY using the Neo4j results provided to you.

Rules:
- Never invent information.
- If multiple rows contain matching people, movies, or facts, include ALL of them.
- Do NOT use "either X or Y" when both X and Y appear in the Neo4j results.
- Treat multiple returned rows as multiple valid facts.
- Keep answers short and natural.
- Do not output HTML.
- Do not output Markdown headings.
- Do not output the word "Answer:".
- If no results are found, clearly say that the information was not found.

Example:

Neo4j results:
Lilly Wachowski
Lana Wachowski

Correct:
"The Matrix was directed by Lana Wachowski and Lilly Wachowski."

Incorrect:
"The Matrix was directed by either Lana Wachowski or Lilly Wachowski."
"""


class RAGEngine:

    def __init__(self):
        self.neo4j = Neo4jClient()

    def ask(self, question):

        # Step 1: Convert question to Cypher
        cypher = question_to_cypher(question)

        # Step 2: Execute Cypher against Neo4j
        results = self.neo4j.run_query(cypher)

        # Step 3: Generate grounded answer
        context = str(results)

        prompt = f"""
User question:
{question}

Neo4j knowledge graph results:
{context}

Using only the knowledge graph results, answer the user's question.
"""

        answer = ollama_generate(
            prompt,
            system=ANSWER_SYSTEM_PROMPT,
            temperature=0.0
        )

        return {
            "question": question,
            "cypher": cypher,
            "results": results,
            "answer": answer.strip()
        }

    def close(self):
        self.neo4j.close()


if __name__ == "__main__":

    engine = RAGEngine()

    try:
        question = input("Ask a movie question: ")

        response = engine.ask(question)

        print("\nGenerated Cypher:")
        print(response["cypher"])

        print("\nNeo4j Results:")
        print(response["results"])

        print("\nAnswer:")
        print(response["answer"])

    except Exception as e:
        print("\nError:")
        print(e)

    finally:
        engine.close()