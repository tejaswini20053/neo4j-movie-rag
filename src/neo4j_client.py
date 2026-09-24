import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


class Neo4jClient:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD)
        )

    def run_query(self, cypher):
        with self.driver.session(database=DATABASE) as session:
            result = session.run(cypher)
            return [record.data() for record in result]

    def close(self):
        self.driver.close()


if __name__ == "__main__":

    client = Neo4jClient()

    try:
        query = """
        MATCH (p:Person)-[:DIRECTED]->(m:Movie)
        WHERE toLower(m.title) = toLower('The Matrix')
        RETURN p.name AS director
        """

        results = client.run_query(query)

        print("Query results:")
        for row in results:
            print(row)

    except Exception as e:
        print("Neo4j error:")
        print(e)

    finally:
        client.close()