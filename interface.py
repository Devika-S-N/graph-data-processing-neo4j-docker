from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, last_node):

        single_target = not isinstance(last_node, (list, tuple))
        targets = [int(last_node)] if single_target else [int(t) for t in last_node]
        s_name = int(start_node)

        def solve_one(session, s, t):
            # Ensure both nodes exist
            ex = session.run("""
                MATCH (s:Location {name: $s})
                OPTIONAL MATCH (t:Location {name: $t})
                RETURN count(s) AS sc, count(t) AS tc
            """, {"s": s, "t": t}).single()
            if not ex or ex["sc"] == 0 or ex["tc"] == 0:
                return {"path": []}

            row = session.run("""
                MATCH (s:Location {name: $s}), (t:Location {name: $t})
                OPTIONAL MATCH p = shortestPath( (s)-[:TRIP*..50]->(t) )
                RETURN CASE
                        WHEN p IS NULL THEN []
                        ELSE [n IN nodes(p) | {name: toInteger(n.name)}]
                    END AS path
            """, {"s": s, "t": t}).single()

            return {"path": row["path"] if row else []}

        results = []
        with self._driver.session() as session:
            for t in targets:
                results.append(solve_one(session, s_name, t))

        return results if not single_target else [results[0]]
    

    def pagerank(self, max_iterations, weight_property):

        graph_name = "pagerank_graph"
        
        with self._driver.session() as session:
            
            # To drop the graph if it exists
            session.run(f"""
                CALL gds.graph.exists('{graph_name}') YIELD exists
                WITH exists
                WHERE exists
                CALL gds.graph.drop('{graph_name}') YIELD graphName
                RETURN 'Dropped ' + graphName AS result
            """)

            # To project the graph using CYPHER PROJECTION            
            node_query = "MATCH (n:Location) RETURN id(n) AS id"
            
            rel_query = f"""
                MATCH (n:Location)-[r:TRIP]->(m:Location)
                WHERE r.{weight_property} > 0
                RETURN id(n) AS source, id(m) AS target, r.{weight_property} AS weight
            """

            session.run(f"""
                CALL gds.graph.project.cypher(
                    '{graph_name}',
                    '{node_query}',
                    '{rel_query}'
                ) YIELD graphName
                RETURN graphName
            """)

            # To run GDS PageRank for the MAX score
            max_query = f"""
                CALL gds.pageRank.stream('{graph_name}', {{
                    maxIterations: $iters,
                    dampingFactor: $damping,
                    tolerance: $tol,
                    relationshipWeightProperty: 'weight'
                }})
                YIELD nodeId, score
                WITH gds.util.asNode(nodeId) AS node, score
                RETURN toInteger(node.name) AS name, score
                ORDER BY score DESC
                LIMIT 1
            """
            max_result = session.run(max_query, {
                "iters": int(max_iterations),
                "damping": 0.85,
                "tol": 0.0
            }).single()

            # To run GDS PageRank for the MIN score
            min_query = f"""
                CALL gds.pageRank.stream('{graph_name}', {{
                    maxIterations: $iters,
                    dampingFactor: $damping,
                    tolerance: $tol,
                    relationshipWeightProperty: 'weight'
                }})
                YIELD nodeId, score
                WITH gds.util.asNode(nodeId) AS node, score
                RETURN toInteger(node.name) AS name, score
                ORDER BY score ASC
                LIMIT 1
            """
            min_result = session.run(min_query, {
                "iters": int(max_iterations),
                "damping": 0.85,
                "tol": 0.0
            }).single()

            # To clean up by dropping the projected graph
            session.run(f"CALL gds.graph.drop('{graph_name}') YIELD graphName")

            # To format and return the results
            if not max_result or not min_result:
                 return [
                    {"name": 0, "score": 0.0},
                    {"name": 0, "score": 0.0},
                 ]

            return [
                {"name": int(max_result["name"]), "score": float(max_result["score"])},
                {"name": int(min_result["name"]), "score": float(min_result["score"])},
            ]
