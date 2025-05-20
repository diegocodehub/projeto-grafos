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


def clarke_wright(v0, Q, servicos_req, grafo):
    # Calcula todos os menores caminhos a partir de cada nó relevante
    nos_relevantes = set([v0])
    for sid, (i, j), c, q, tp in servicos_req:
        nos_relevantes.add(i)
        nos_relevantes.add(j)
    menor_caminho = {}
    for u in nos_relevantes:
        dist, _ = dijkstra(grafo, u)
        menor_caminho[u] = dist
    # Inicialmente, cada serviço é uma rota separada
    rotas = []
    seq_ids_por_rota = []
    demanda_rota = []
    for sid, (i, j), c, q, tp in servicos_req:
        rota = [v0, i, j, v0]
        rotas.append(rota)
        seq_ids_por_rota.append([sid])
        demanda_rota.append(q)
    # Savings: economia ao unir duas rotas
    savings = []
    n = len(servicos_req)
    for a in range(n):
        for b in range(a+1, n):
            sid_a, (i_a, j_a), c_a, q_a, _ = servicos_req[a]
            sid_b, (i_b, j_b), c_b, q_b, _ = servicos_req[b]
            # Economia ao unir rota_a e rota_b
            saving = menor_caminho[j_a][v0] + menor_caminho[v0][i_b] - menor_caminho[j_a][i_b]
            savings.append((saving, a, b))
    # Ordena por maior economia
    savings.sort(reverse=True)
    # Estrutura para saber a qual rota cada serviço pertence
    rota_de = list(range(n))
    for saving, a, b in savings:
        ra = rota_de[a]
        rb = rota_de[b]
        if ra == rb:
            continue
        if demanda_rota[ra] + demanda_rota[rb] > Q:
            continue
        # Une as rotas
        nova_seq = seq_ids_por_rota[ra] + seq_ids_por_rota[rb]
        nova_demanda = demanda_rota[ra] + demanda_rota[rb]
        seq_ids_por_rota[ra] = nova_seq
        demanda_rota[ra] = nova_demanda
        for idx in seq_ids_por_rota[rb]:
            rota_de[servicos_req.index(next(s for s in servicos_req if s[0]==idx))] = ra
        seq_ids_por_rota[rb] = []
        demanda_rota[rb] = 0
    # Remove rotas vazias
    rotas_finais = []
    seqs_finais = []
    for seq in seq_ids_por_rota:
        if seq:
            rota = [v0]
            atual = v0
            for sid in seq:
                _, i, j, _, _ = next(s for s in servicos_req if s[0]==sid)
                # Garante que i e j são inteiros
                if isinstance(i, tuple):
                    i = i[0]
                if isinstance(j, tuple):
                    j = j[0]
                # Caminho do atual até i
                _, pai = dijkstra(grafo, atual)
                caminho = reconstruir_caminho(pai, i)
                rota += caminho[1:] if len(caminho) > 1 else []
                rota.append(j)
                atual = j
            # Volta ao depósito
            _, pai = dijkstra(grafo, atual)
            caminho = reconstruir_caminho(pai, v0)
            rota += caminho[1:] if len(caminho) > 1 else []
            rotas_finais.append(rota)
            seqs_finais.append(seq)
    return rotas_finais, seqs_finais


def resolver_problema(v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr):
    # Monta lista de serviços requeridos
    servicos = []
    id_s = 1
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
        servicos.append((id_s, (i, i), 0, q, 'N'))
        info_serv[id_s] = ('N', i, i)
        custo_serv_dict[id_s] = q
        id_s += 1
    # Adiciona não requeridos como conexões sem demanda
    for (i, j), c in arestas_nr:
        servicos.append((0, (i, j), c, 0, 'E'))
    for (i, j), c in arcos_nr:
        servicos.append((0, (i, j), c, 0, 'A'))
    # Grafo para deslocamento (lista de adjacência)
    grafo = construir_grafo(servicos)
    servicos_req = [s for s in servicos if s[0] != 0]
    # Aplica Clarke-Wright
    rotas, seq_ids_por_rota = clarke_wright(v0, Q, servicos_req, grafo)
    # Calcula custos
    custo_d = 0
    custo_s = 0
    for rota, seq in zip(rotas, seq_ids_por_rota):
        visitados = set()
        for sid in seq:
            if sid not in visitados:
                custo_s += custo_serv_dict[sid]
                visitados.add(sid)
        for u, v in zip(rota, rota[1:]):
            if (u, v) in custos_desloc:
                custo_d += custos_desloc[(u, v)]
    return rotas, seq_ids_por_rota, custo_d, custo_s