# Neo4j Movie Graph RAG

A small RAG app: Neo4j movie knowledge graph + a local Ollama LLM
(`qwen3:1.7b`) that turns your questions into Cypher, runs them, and answers
in plain English. Comes with a CLI and a Streamlit web UI.

```
neo4j-movie-rag/
├── README.md                       <- you are here
├── requirements.txt
├── .env.example
├── app.py                          <- Streamlit web UI
├── setup/
│   └── load_movie_dataset.cypher   <- dataset loader (run this first)
├── docs/
│   ├── cypher_query_templates.md   <- reusable Cypher templates
│   └── PROJECT_REPORT.md           <- schema, architecture, examples, limitations
└── src/
    ├── config.py
    ├── neo4j_client.py
    ├── llm_client.py               <- talks to Ollama
    ├── nl2cypher.py                <- question -> Cypher
    ├── rag_engine.py                <- orchestration
    └── cli.py
```

You already have Ollama with `qwen3:1.7b` pulled. You said you don't have the
dataset — Step 3 below creates it for you (no download needed).

---

## Step 1 — Install Neo4j and start a database

Pick ONE:

**Option A: Neo4j Desktop (recommended, free, local)**
1. Download from https://neo4j.com/download/ and install.
2. Open Neo4j Desktop → "New Project" → "Add" → "Local DBMS".
3. Set a password (remember it — you'll need it in `.env`).
4. Click "Start" on the DBMS. Once it's running, click "Open" → Neo4j Browser.

**Option B: Neo4j AuraDB Free (cloud, no install)**
1. Go to https://neo4j.com/cloud/aura-free/ and create a free instance.
2. Save the generated password and the `neo4j+s://...` connection URI shown
   during creation — you'll need both.

## Step 2 — Load the movie dataset

1. Open **Neo4j Browser** (Desktop: click "Open" on your DBMS; Aura: use the
   "Query" tab in the Aura console).
2. Open `setup/load_movie_dataset.cypher` from this project in a text editor,
   copy its entire contents, paste into the Neo4j Browser query box, and run
   it (▶ button, or `Ctrl+Enter`).
3. Verify it worked — run this in the browser:
   ```cypher
   MATCH (m:Movie) RETURN count(m);
   ```
   You should see `15`.

   (Alternative for Neo4j Desktop only: typing `:play movies` in the browser
   and clicking through gives you Neo4j's official larger demo dataset if you
   want more data — either works with this app since the schema matches.)

## Step 3 — Configure the app

```bash
cd neo4j-movie-rag
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `.env`:
- `NEO4J_URI` — `bolt://localhost:7687` for Desktop, or the `neo4j+s://...`
  URI Aura gave you.
- `NEO4J_USER` — usually `neo4j`.
- `NEO4J_PASSWORD` — the password you set in Step 1.
- `OLLAMA_MODEL` — leave as `qwen3:1.7b` (matches what you already have).
- `OLLAMA_HOST` — leave as `http://localhost:11434` unless Ollama runs
  elsewhere.

## Step 4 — Make sure Ollama is serving the model

```bash
ollama serve          # if it isn't already running as a service
ollama list            # confirm qwen3:1.7b is listed
```

## Step 5 — Run it

**Web UI (recommended):**
```bash
streamlit run app.py
```
Opens at http://localhost:8501 — type a question, see the generated Cypher,
the raw graph rows, and the natural-language answer.

**CLI:**
```bash
python -m src.cli
```
Type questions at the `You:` prompt; type `schema` to see the graph schema,
`exit` to quit.

## Step 6 — Try it

```
Who directed The Matrix?
What movies did Tom Hanks act in?
Who co-starred with Keanu Reeves in The Matrix?
What are the best reviewed movies?
Which movies were released after 2000?
```

## Troubleshooting
- **"Could not connect to Neo4j"** — confirm the DBMS is started (Desktop)
  and the URI/password in `.env` are correct.
- **"Ollama: not reachable"** — run `ollama serve` in a terminal and keep it
  running while you use the app.
- **Weird / broken Cypher from the model** — `qwen3:1.7b` is small; the app
  already blocks destructive queries and shows execution errors instead of
  crashing. Rephrase the question more literally (closer to the example
  questions above) if it struggles.
- **Empty answers** — run `schema` (CLI) or click "Show graph schema"
  (Streamlit sidebar) to confirm the dataset loaded correctly in Step 2.

See `docs/PROJECT_REPORT.md` for the full write-up (schema, RAG architecture
diagram, example interactions, limitations, and possible extensions) and
`docs/cypher_query_templates.md` for the reusable Cypher templates.
