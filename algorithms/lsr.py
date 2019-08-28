import json

def lsr(session, msg):
    print('in algorithm: ', session.lsps)
    lsp = json.loads(msg['body'])
    print(lsp)
    graph = session.graph
    if lsp["node"] in session.lsps:
        if lsp["serial"] <= session.lsps[lsp["node"]]["serial"]:
            return False
        else:
            for node in lsp["neighbourhood"]:
                graph.addEdge(lsp["node"], node, lsp["neighbourhood"][node])
            session.lsps[lsp["node"]] = lsp
            return msg['body']
    elif lsp["node"] == session.name:
        return False
    else:
        session.lsps[lsp["node"]] = lsp
        for node in lsp["neighbourhood"]:
            graph.addNode(node)
            graph.addEdge(lsp["node"], node, lsp["neighbourhood"][node])
        return msg['body']
