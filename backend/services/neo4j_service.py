from datetime import datetime, timezone

from neo4j import GraphDatabase

from config import settings

_driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
)


def close():
    _driver.close()


def get_entity_neighbours(tag: str) -> dict:
    """Fetch an entity with its 1-hop neighbours and their state_history."""
    query = (
        "MATCH (n:Entity {tag: $tag}) "
        "OPTIONAL MATCH (n)-[r]-(m:Entity) "
        "RETURN n AS node, collect(DISTINCT {rel: type(r), neighbour: m}) AS neighbours"
    )
    with _driver.session() as session:
        record = session.run(query, tag=tag).single()
        if not record or record["node"] is None:
            return {}
        neighbours = []
        for item in record["neighbours"]:
            if item["neighbour"] is not None:
                neighbours.append(
                    {"rel": item["rel"], "entity": dict(item["neighbour"])}
                )
        return {"entity": dict(record["node"]), "neighbours": neighbours}


def upsert_entity_node(tag: str, node_type: str, properties: dict) -> dict:
    """Create or update an entity node, merging properties and keeping a state_history list."""
    query = (
        "MERGE (n:Entity {tag: $tag}) "
        "ON CREATE SET n.created_at = $now, n.state_history = [] "
        "SET n.node_type = $node_type, n.updated_at = $now, n += $properties "
        "RETURN n"
    )
    with _driver.session() as session:
        record = session.run(
            query,
            tag=tag,
            node_type=node_type,
            properties=properties or {},
            now=datetime.now(timezone.utc).isoformat(),
        ).single()
        return dict(record["n"]) if record else {}


def add_state_transition(tag: str, transition_dict: dict) -> dict:
    """Append a state transition (as a serialized entry) to an entity's state_history."""
    entry = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **transition_dict,
    }
    serialized = {k: str(v) for k, v in entry.items()}
    query = (
        "MERGE (n:Entity {tag: $tag}) "
        "ON CREATE SET n.created_at = $now, n.state_history = [] "
        "SET n.state_history = coalesce(n.state_history, []) + $entry, "
        "n.updated_at = $now "
        "RETURN n"
    )
    with _driver.session() as session:
        record = session.run(
            query,
            tag=tag,
            entry=[str(serialized)],
            now=datetime.now(timezone.utc).isoformat(),
        ).single()
        return dict(record["n"]) if record else {}


def get_all_nodes() -> list[dict]:
    """Return all entity nodes as a list of dicts (tag, type, state_history, criticality)."""
    query = (
        "MATCH (n:Entity) "
        "RETURN n.tag AS tag, n.node_type AS type, "
        "n.state_history AS state_history, n.criticality AS criticality"
    )
    with _driver.session() as session:
        records = session.run(query).data()
    return [
        {
            "tag": r["tag"],
            "type": r["type"],
            "state_history": r["state_history"] or [],
            "criticality": r["criticality"] or "unknown",
        }
        for r in records
    ]


def get_node_with_neighbours(tag: str) -> dict:
    """Return a single node with its full state timeline and 1-hop neighbours."""
    graph = get_entity_neighbours(tag)
    if not graph:
        return {}
    entity = graph["entity"]
    return {
        "tag": entity.get("tag", tag),
        "type": entity.get("node_type"),
        "criticality": entity.get("criticality", "unknown"),
        "state_history": entity.get("state_history", []),
        "neighbours": graph["neighbours"],
    }


def export_graph_d3() -> dict:
    """Export the full graph in D3 JSON shape: {nodes: [...], edges: [...]}."""
    node_query = (
        "MATCH (n:Entity) "
        "RETURN n.tag AS id, n.tag AS label, n.node_type AS type, "
        "n.criticality AS criticality"
    )
    edge_query = (
        "MATCH (a:Entity)-[r]->(b:Entity) "
        "RETURN a.tag AS source, b.tag AS target, type(r) AS relationship"
    )
    with _driver.session() as session:
        node_records = session.run(node_query).data()
        edge_records = session.run(edge_query).data()
    nodes = [
        {
            "id": r["id"],
            "label": r["label"],
            "type": r["type"],
            "criticality": r["criticality"] or "unknown",
        }
        for r in node_records
    ]
    edges = [
        {
            "source": r["source"],
            "target": r["target"],
            "relationship": r["relationship"],
        }
        for r in edge_records
    ]
    return {"nodes": nodes, "edges": edges}


def get_equipment_timeline(tag: str) -> list:
    """Return the state_history list for a single equipment tag."""
    query = "MATCH (n:Entity {tag: $tag}) RETURN n.state_history AS state_history"
    with _driver.session() as session:
        record = session.run(query, tag=tag).single()
    if not record or record["state_history"] is None:
        return []
    return record["state_history"]
