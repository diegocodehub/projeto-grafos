import heapq
from collections import defaultdict

# Globais para mapeamento de serviços
info_serv = {}
custo_serv_dict = {}
custos_desloc = {}


def dijkstra(grafo, origem):
    dist = {v: float('inf') for v in grafo}
    dist[origem] = 0
    pai = {v: None for v in grafo}
    fila = [(0, origem)]
    while fila:
        d, u = heapq.heappop(fila)
        if d > dist[u]:
            continue
        for v, c in grafo[u]:
            if dist[v] > d + c:
                dist[v] = d + c
                pai[v] = u
                heapq.heappush(fila, (dist[v], v))
    return dist, pai


def reconstruir_caminho(pai, destino):
    caminho = []
    while destino is not None:
        caminho.append(destino)
        destino = pai[destino]
    return caminho[::-1]


def construir_grafo(services):
    grafo = defaultdict(list)
    for sid, (i, j), c, q, tp in services:
        custos_desloc[(i, j)] = c
        grafo[i].append((j, c))
        if tp == 'E':
            custos_desloc[(j, i)] = c
            grafo[j].append((i, c))
    return grafo


def resolver_problema(v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr):
    servicos = []
    id_s = 1
    # requeridos
    for (i, j), c, q in arestas_req:
        servicos.append((id_s, (i, j), c, q, 'E'))
        info_serv[id_s] = ('E', i, j)
        custo_serv_dict[id_s] = q
        id_s += 1
    for (i, j), c, q in arcos_req:
        servicos.append((id_s, (i, j), c, q, 'A'))
        info_serv[id_s] = ('A', i, j)
        custo_serv_dict[id_s] = q
        id_s += 1
    for i, q in nos:
        servicos.append((id_s, (v0, i), 0, q, 'N'))
        info_serv[id_s] = ('N', i, i)
        custo_serv_dict[id_s] = q
        id_s += 1

    # adiciona não requeridos como conexões sem demanda
    for (i, j), c in arestas_nr:
        servicos.append((0, (i, j), c, 0, 'E'))
    for (i, j), c in arcos_nr:
        servicos.append((0, (i, j), c, 0, 'A'))

    grafo = construir_grafo(servicos)

    servicos_req = [s for s in servicos if s[0] != 0]
    servicos_req.sort(key=lambda x: x[2])

    atendidos = set()
    rotas = []
    seq_ids_por_rota = []
    custo_d = 0
    custo_s = 0

    while len(atendidos) < len(servicos_req):
        carga = 0
        rota = [v0]
        seq = []
        atual = v0
        for sid, (i, j), c, q, tp in servicos_req:
            if sid in atendidos or carga + q > Q:
                continue
            dist, pai = dijkstra(grafo, atual)
            if dist[i] == float('inf'):
                continue
            caminho = reconstruir_caminho(pai, i)
            rota += caminho[1:]
            custo_d += dist[i]
            rota.append(j)
            carga += q
            custo_s += q
            atendidos.add(sid)
            seq.append(sid)
            atual = j
        if atual != v0:
            dist, pai = dijkstra(grafo, atual)
            caminho = reconstruir_caminho(pai, v0)
            rota += caminho[1:]
            custo_d += dist[v0]
        rotas.append(rota)
        seq_ids_por_rota.append(seq)

    return rotas, seq_ids_por_rota, custo_d, custo_s