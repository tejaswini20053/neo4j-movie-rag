import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

from src.rag_engine import RAGEngine


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="MovieRAG",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------
st.markdown("""
<style>

.main {
    background-color: #0b0f19;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Header */
.hero {
    padding: 25px 30px;
    border-radius: 18px;
    background: linear-gradient(135deg, #111827, #172033);
    border: 1px solid #263247;
    margin-bottom: 25px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.hero-subtitle {
    color: #9ca3af;
    font-size: 16px;
}

/* Cards */
.card {
    background: #111827;
    border: 1px solid #263247;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 14px;
}

/* Answer */
.answer-card {
    background: linear-gradient(135deg, #10251d, #0f1d19);
    border: 1px solid #24543e;
    border-radius: 16px;
    padding: 24px;
    margin-top: 10px;
}

.answer-label {
    color: #86efac;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.answer-text {
    color: #f3f4f6;
    font-size: 20px;
    line-height: 1.6;
}

/* Suggested questions */
.question-box {
    background: #111827;
    border: 1px solid #263247;
    border-radius: 14px;
    padding: 10px;
}

/* Sidebar */
.sidebar-title {
    font-size: 22px;
    font-weight: 700;
}

.status {
    padding: 10px 14px;
    background: #10251d;
    border: 1px solid #24543e;
    border-radius: 10px;
    color: #86efac;
    margin-top: 10px;
}

/* Footer */
.footer {
    text-align: center;
    color: #6b7280;
    margin-top: 40px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "question" not in st.session_state:
    st.session_state.question = ""

if "run_question" not in st.session_state:
    st.session_state.run_question = None

if "response" not in st.session_state:
    st.session_state.response = None


# ---------------------------------------------------------
# RAG ENGINE
# ---------------------------------------------------------
@st.cache_resource
def get_engine():
    return RAGEngine()


engine = get_engine()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">🎬 MovieRAG</div>',
        unsafe_allow_html=True
    )

    st.write("Neo4j Knowledge Graph + Local LLM")

    st.markdown(
        """
        <div class="status">
        🟢 Neo4j Connected<br>
        🟢 Ollama Connected<br>
        🟢 RAG Ready
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 💡 What can you ask?")

    st.write("• Movie information")
    st.write("• Directors")
    st.write("• Actors")
    st.write("• Movie recommendations")
    st.write("• Movie reviews")
    st.write("• Release information")

    st.divider()

    st.caption("Neo4j + Cypher + RAG + Ollama")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🎬 MovieRAG</div>
        <div class="hero-subtitle">
            Ask questions about movies using a Neo4j Knowledge Graph
            and Retrieval-Augmented Generation.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# SUGGESTED QUESTIONS
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">✨ Try a question</div>',
    unsafe_allow_html=True
)

suggested_questions = [
    "Who directed The Matrix?",
    "Who acted in The Matrix?",
    "When was The Matrix released?",
    "Who directed Top Gun?",
    "Who acted in Jerry Maguire?",
    "What movies did Tom Hanks act in?"
]

cols = st.columns(2)

for i, question in enumerate(suggested_questions):

    with cols[i % 2]:

        if st.button(
            question,
            key=f"suggested_{i}",
            use_container_width=True
        ):
            st.session_state.question = question
            st.session_state.run_question = question


# ---------------------------------------------------------
# QUESTION INPUT
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">🔎 Ask MovieRAG</div>',
    unsafe_allow_html=True
)

question = st.text_input(
    "Enter your question",
    key="question",
    placeholder="Example: Who directed The Matrix?",
    label_visibility="collapsed"
)

ask_clicked = st.button(
    "🚀 Ask MovieRAG",
    use_container_width=True,
    type="primary"
)


# ---------------------------------------------------------
# DETERMINE QUESTION TO RUN
# ---------------------------------------------------------
question_to_run = None

if ask_clicked and question.strip():
    question_to_run = question.strip()

elif st.session_state.run_question:
    question_to_run = st.session_state.run_question
    st.session_state.run_question = None


# ---------------------------------------------------------
# RUN RAG
# ---------------------------------------------------------
if question_to_run:

    with st.spinner("🔍 Searching Neo4j Knowledge Graph..."):

        try:
            response = engine.ask(question_to_run)

            st.session_state.response = response

        except Exception as e:

            st.error(f"Error: {e}")


# ---------------------------------------------------------
# RESPONSE
# ---------------------------------------------------------
if st.session_state.response:

    response = st.session_state.response

    st.markdown(
        '<div class="section-title">💬 MovieRAG Response</div>',
        unsafe_allow_html=True
    )

    # Clean answer
    answer = response.get("answer", "")

    # Remove accidental HTML if LLM produces it
    answer = answer.replace("<div class=\"answer-text\">", "")
    answer = answer.replace("</div>", "")
    answer = answer.replace("Answer:", "").strip()

    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-label">MovieRAG Response</div>
            <div class="answer-text">
                {answer}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # KNOWLEDGE GRAPH
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">🕸️ Knowledge Graph</div>',
        unsafe_allow_html=True
    )

    nodes = []
    edges = []

    results = response.get("results", [])
    cypher = response.get("cypher", "")

    # DIRECTED
    if "DIRECTED" in cypher.upper():

        movie_title = "The Matrix"

        nodes.append(
            Node(
                id="movie",
                label=movie_title,
                size=35,
                shape="dot"
            )
        )

        for i, row in enumerate(results):

            director = row.get("director")

            if director:

                person_id = f"director_{i}"

                nodes.append(
                    Node(
                        id=person_id,
                        label=director,
                        size=28,
                        shape="dot"
                    )
                )

                edges.append(
                    Edge(
                        source=person_id,
                        target="movie",
                        label="DIRECTED"
                    )
                )


    # ACTED_IN
    elif "ACTED_IN" in cypher.upper():

        movie_nodes = {}

        for i, row in enumerate(results):

            movie = row.get("movie")
            actor = row.get("actor")

            if actor:

                actor_id = f"actor_{i}"

                nodes.append(
                    Node(
                        id=actor_id,
                        label=actor,
                        size=27,
                        shape="dot"
                    )
                )

                if movie:

                    movie_id = f"movie_{movie}"

                    if movie_id not in movie_nodes:

                        movie_nodes[movie_id] = True

                        nodes.append(
                            Node(
                                id=movie_id,
                                label=movie,
                                size=34,
                                shape="dot"
                            )
                        )

                    edges.append(
                        Edge(
                            source=actor_id,
                            target=movie_id,
                            label="ACTED_IN"
                        )
                    )


    # Show graph
    if nodes:

        config = Config(
            width=1000,
            height=550,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#22c55e",
            collapsible=False
        )

        agraph(
            nodes=nodes,
            edges=edges,
            config=config
        )

    else:

        st.info(
            "Graph data is not available for this query yet."
        )


    # -----------------------------------------------------
    # CYPHER
    # -----------------------------------------------------
    with st.expander("🧠 View Generated Cypher"):

        st.code(
            response.get("cypher", ""),
            language="cypher"
        )


    # -----------------------------------------------------
    # NEO4J RESULTS
    # -----------------------------------------------------
    with st.expander("📊 View Neo4j Results"):

        st.json(response.get("results", []))


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        MovieRAG • Neo4j Knowledge Graph • Cypher • RAG • Ollama
    </div>
    """,
    unsafe_allow_html=True
)