"""Read-only graph tool surface available to the local agent."""

def downstream(graph, entity: str, depth: int | None = None):
    return graph.downstream(entity, depth)

def upstream(graph, entity: str, depth: int | None = None):
    return graph.upstream(entity, depth)
