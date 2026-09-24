# Project Report: Neo4j Movie Graph RAG Application

## 1. Problem Statement
Design and implement a small Retrieval-Augmented Generation (RAG) application
that uses the Neo4j Movies dataset as a knowledge graph backend, retrieves
relevant movie/actor/director information via Cypher queries, and uses an LLM
to generate grounded natural-language answers to user questions.

## 2. Knowledge Graph Schema
Two node labels and six relationship types:

```
(:Person {name, born})
(:Movie  {title, released, tagline})

(:Person)-[:ACTED_IN   {roles: [string]}]->(:Movie)
(:Person)-[:DIRECTED                    ]->(:Movie)
(:Person)-[:PRODUCED                    ]->(:Movie)
(:Person)-[:WROTE                       ]->(:Movie)
(:Person)-[:REVIEWED   {summary, rating}]->(:Movie)
(:Person)-[:FOLLOWS                     ]->(:Person)
```

ASCII sketch:

```
 (Person)-- ACTED_IN{roles} -->(Movie)
 (Person)-- DIRECTED -------->(Movie)
 (Person)-- PRODUCED -------->(Movie)
 (Person)-- WROTE ----------->(Movie)
 (Person)-- REVIEWED{rating}->(Movie)
 (Person)-- FOLLOWS --------->(Person)
```

`load_movie_dataset.cypher` (in `setup/`) populates this schema with ~15
movies and ~35 people, based on the classic Neo4j movie-graph tutorial data.

## 3. RAG Architecture

```
 ┌──────────────┐   question   ┌───────────────────┐  Cypher  ┌─────────┐
 │  User (CLI /  │ ───────────▶│  nl2cypher.py      │ ───────▶│  Neo4j  │
 │  Streamlit)   │              │  (LLM: schema-     │         │  Graph  │
 │               │              │  grounded prompt)  │         └────┬────┘
 │               │              └───────────────────┘              │ rows
 │               │◀────────────  rag_engine.py  ◀───────────────────┘
 │               │   NL answer   (LLM: answer from rows only)
 └──────────────┘
```

Steps for every question:
1. **Retrieve schema** — labels/relationship types are known up front (static
   prompt) so the small model doesn't have to guess field names.
2. **Generate Cypher** — `nl2cypher.py` sends the question + schema + few-shot
   examples to the local Ollama model (`qwen3:1.7b`), gets back one Cypher
   query, strips markdown fences, and rejects any write/delete keywords.
3. **Retrieve (Cypher execution)** — the query runs against Neo4j via the
   official Python driver; rows come back as plain dicts.
4. **Augmented generation** — the question and the retrieved rows (not the
   whole graph) are sent back to the LLM with instructions to answer only
   from that data, producing a grounded natural-language answer.
5. **Present** — CLI prints Cypher / rows / answer; the Streamlit UI shows
   the same three plus a schema viewer and example questions.

This is the standard "text-to-Cypher RAG" pattern: instead of embedding text
chunks in a vector store, the "retrieval" step is a generated structured
query against a graph, which is well suited to a densely relational dataset
like a movie graph (who acted with whom, shortest path between actors, etc.).

## 4. Example Interactions

| Question | Generated Cypher (abridged) | Answer |
|---|---|---|
| Who directed The Matrix? | `MATCH (p)-[:DIRECTED]->(m:Movie{title:'The Matrix'}) RETURN p.name` | The Matrix was directed by Lana Wachowski and Lilly Wachowski. |
| What movies did Tom Hanks act in? | `MATCH (p:Person{name:'Tom Hanks'})-[:ACTED_IN]->(m) RETURN m.title, m.released` | Tom Hanks appears in Sleepless in Seattle, You've Got Mail, Cloud Atlas, and The Da Vinci Code. |
| Who co-starred with Keanu Reeves in The Matrix? | `MATCH (keanu)-[:ACTED_IN]->(m)<-[:ACTED_IN]-(costar) ...` | Carrie-Anne Moss, Laurence Fishburne, and Hugo Weaving co-starred with Keanu Reeves. |
| What are the best reviewed movies? | `MATCH (:Person)-[r:REVIEWED]->(m) RETURN m.title, r.rating ORDER BY r.rating DESC` | The Matrix has the highest rating (95), followed by Sleepless in Seattle (85). |

(Exact answers depend on the LLM's phrasing each run; the underlying data is
deterministic since it comes straight from Cypher.)

## 5. Limitations
- A 1.7B-parameter model occasionally produces malformed Cypher for complex,
  multi-hop, or ambiguous questions — the app catches execution errors and
  reports them rather than guessing.
- No conversation memory: each question is handled independently.
- Schema is summarized generically (labels/rel types), not per-query few-shot
  retrieval — larger graphs would benefit from retrieving only the relevant
  schema slice.
- The write-query guard is a keyword blocklist, not a formal read-only Neo4j
  role; for production use, connect with a read-only database user as well.
- No entity disambiguation — "Tom" won't automatically resolve to "Tom Hanks"
  vs "Tom Cruise"; the LLM guesses from context.

## 6. Possible Extensions
- Add a vector index over `Movie.tagline`/`REVIEWED.summary` for hybrid
  semantic + graph retrieval (true "GraphRAG").
- Add conversation memory so follow-up questions ("what else did he direct?")
  resolve pronouns.
- Swap the keyword blocklist for a Neo4j read-only role/user.
- Add query result caching and a feedback loop (thumbs up/down) to build a
  few-shot example bank from real usage.
- Expand the dataset via `LOAD CSV` from a larger movie dataset (e.g.
  MovieLens) instead of the hand-authored demo graph.

## 7. Tools Used
- **Neo4j Desktop** (or Neo4j AuraDB Free) — graph database
- **Ollama** running `qwen3:1.7b` — local LLM for NL→Cypher and answer generation
- **Python** (`neo4j` driver, `requests`, `python-dotenv`)
- **Streamlit** — web UI (a CLI is also provided)
