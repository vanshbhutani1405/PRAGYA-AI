from fastapi import APIRouter, HTTPException

from services import neo4j_service
from services.neo4j_service import _driver

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.get("/nodes")
async def list_nodes():
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


@router.get("/nodes/{tag}")
async def get_node(tag: str):
    graph = neo4j_service.get_entity_neighbours(tag)
    if not graph:
        raise HTTPException(status_code=404, detail="Node not found")
    entity = graph["entity"]
    return {
        "tag": entity.get("tag", tag),
        "type": entity.get("node_type"),
        "criticality": entity.get("criticality", "unknown"),
        "state_history": entity.get("state_history", []),
        "neighbours": graph["neighbours"],
    }


@router.get("/export")
async def export_graph():
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
