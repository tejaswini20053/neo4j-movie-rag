import re
from src.llm_client import ollama_generate


SYSTEM_PROMPT = """You are a Neo4j Cypher expert.

You convert a user's natural language question about a movie knowledge graph
into a single, syntactically correct Cypher query.

Graph schema:
  (:Person {name})
  (:Movie {title, released, tagline})
  (:Person)-[:ACTED_IN {roles}]->(:Movie)
  (:Person)-[:DIRECTED]->(:Movie)
  (:Person)-[:PRODUCED]->(:Movie)
  (:Person)-[:WROTE]->(:Movie)
  (:Person)-[:REVIEWED {summary, rating}]->(:Movie)
  (:Person)-[:FOLLOWS]->(:Person)

Rules:
- Output ONLY the Cypher query.
- No explanation.
- No markdown fences.
- No comments.
- Always end with a RETURN clause.
- Never write, delete, or modify data.
- Do not use CREATE, MERGE, SET, DELETE, DROP, or REMOVE.
- Use case-insensitive matching for names and titles.
- Prefer LIMIT 25 for queries that could return many rows.
- Whenever a query retrieves relationships between nodes, RETURN the
  actual source node, relationship, and target node as:
  source_node, relationship, target_node.

- Also return normal display fields needed for the answer.

Examples:

Question:
Who directed The Matrix?

Cypher:
MATCH (p:Person)-[r:DIRECTED]->(m:Movie)
WHERE toLower(m.title) = toLower('The Matrix')
RETURN p AS source_node,
       r AS relationship,
       m AS target_node,
       p.name AS director

Question:
Who acted in The Matrix?

Cypher:
MATCH (p:Person)-[r:ACTED_IN]->(m:Movie)
WHERE toLower(m.title) = toLower('The Matrix')
RETURN p AS source_node,
       r AS relationship,
       m AS target_node,
       p.name AS actor,
       m.title AS movie

Question:
What movies did Tom Hanks act in?

Cypher:
MATCH (p:Person)-[r:ACTED_IN]->(m:Movie)
WHERE toLower(p.name) = toLower('Tom Hanks')
RETURN p AS source_node,
       r AS relationship,
       m AS target_node,
       m.title AS movie,
       m.released AS year


Examples:

Q: Who directed The Matrix?
CYPHER:
MATCH (p:Person)-[:DIRECTED]->(m:Movie)
WHERE toLower(m.title) = toLower('The Matrix')
RETURN p.name AS director

Q: What movies did Tom Hanks act in?
CYPHER:
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
WHERE toLower(p.name) = toLower('Tom Hanks')
RETURN m.title AS movie, m.released AS year
ORDER BY m.released

Q: Who co-starred with Keanu Reeves in The Matrix?
CYPHER:
MATCH (keanu:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(costar:Person)
WHERE toLower(keanu.name) = toLower('Keanu Reeves')
AND toLower(m.title) = toLower('The Matrix')
RETURN DISTINCT costar.name AS costar

Q: What are the best reviewed movies?
CYPHER:
MATCH (:Person)-[r:REVIEWED]->(m:Movie)
RETURN m.title AS movie, r.rating AS rating
ORDER BY r.rating DESC
LIMIT 10
"""


def question_to_cypher(question: str) -> str:
    prompt = f"Q: {question}\nCYPHER:"

    raw = ollama_generate(
        prompt,
        system=SYSTEM_PROMPT,
        temperature=0.0
    )

    return _clean_cypher(raw)


def _clean_cypher(raw: str) -> str:
    """Clean markdown fences and unwanted text from the LLM response."""

    text = raw.strip()

    # Remove markdown code fences
    fence = re.search(
        r"```(?:cypher)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if fence:
        text = fence.group(1).strip()

    # Remove repeated CYPHER: label
    if "CYPHER:" in text:
        text = text.rsplit("CYPHER:", 1)[-1].strip()

    # Prevent destructive queries
    forbidden = (
        "CREATE",
        "MERGE",
        "DELETE",
        "SET ",
        "DROP",
        "REMOVE"
    )

    upper = text.upper()

    if any(token in upper for token in forbidden):
        raise ValueError(
            f"Refusing to run a potentially destructive query: {text}"
        )

    return text


if __name__ == "__main__":
    question = input("Ask a movie question: ")

    cypher = question_to_cypher(question)

    print("\nGenerated Cypher:")
    print(cypher)