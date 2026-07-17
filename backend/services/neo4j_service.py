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
