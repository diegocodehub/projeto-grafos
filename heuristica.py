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


def preparar_clientes(nos, arestas_req, arcos_req):
    clientes = []
    id_servico = 1
    for v, q in nos:
        clientes.append({'tipo': 'n', 'id': id_servico, 'origem': v, 'destino': v, 'demanda': q, 'custo': 0})
        id_servico += 1
    for (u, v), c, q in arestas_req:
        clientes.append({'tipo': 'e', 'id': id_servico, 'origem': u, 'destino': v, 'demanda': q, 'custo': c})
        id_servico += 1
    for (u, v), c, q in arcos_req:
        clientes.append({'tipo': 'a', 'id': id_servico, 'origem': u, 'destino': v, 'demanda': q, 'custo': c})
        id_servico += 1
    return clientes


def inicializar_rotas(clientes, deposito):
    rotas = []
    for cliente in clientes:
        rota = {
            'clientes': [cliente],
            'demanda_total': cliente['demanda'],
            'servicos': {(cliente['tipo'], cliente['id'])},
            'sequencia': [deposito, cliente['origem'], cliente['destino'], deposito]
        }
        rotas.append(rota)
    return rotas


def calcular_savings(rotas, custos_desloc, deposito):
    savings = []
    for i in range(len(rotas)):
        for j in range(len(rotas)):
            if i == j:
                continue
            fim_i = rotas[i]['sequencia'][-2]
            ini_j = rotas[j]['sequencia'][1]
            saving = custos_desloc.get((fim_i, deposito), 0) + custos_desloc.get((deposito, ini_j), 0) - custos_desloc.get((fim_i, ini_j), float('inf'))
            savings.append((saving, i, j))
    return sorted(savings, reverse=True)


def juntar_rotas_iterativamente(rotas, custos_desloc, deposito, capacidade):
    while True:
        melhor_gain = float('-inf')
        melhor_nova_rota = None
        melhor_i = melhor_j = -1
        melhor_tipo = None
        # Testa todas as combinações e tipos de concatenação
        for i in range(len(rotas)):
            for j in range(len(rotas)):
                if i == j:
                    continue
                rota_i = rotas[i]
                rota_j = rotas[j]
                # Checagem de unicidade dos serviços (apenas IDs)
                ids_i = set(c['id'] for c in rota_i['clientes'])
                ids_j = set(c['id'] for c in rota_j['clientes'])
                if ids_i & ids_j:
                    continue
                nova_demanda = rota_i['demanda_total'] + rota_j['demanda_total']
                if nova_demanda > capacidade:
                    continue
                # Fim de i com início de j
                gain1 = custos_desloc.get((rota_i['sequencia'][-2], deposito), 0) + custos_desloc.get((deposito, rota_j['sequencia'][1]), 0) - custos_desloc.get((rota_i['sequencia'][-2], rota_j['sequencia'][1]), float('inf'))
                seq1 = rota_i['sequencia'][:-1] + rota_j['sequencia'][1:]
                # Início de i com fim de j (reverso)
                gain2 = custos_desloc.get((rota_j['sequencia'][-2], deposito), 0) + custos_desloc.get((deposito, rota_i['sequencia'][1]), 0) - custos_desloc.get((rota_j['sequencia'][-2], rota_i['sequencia'][1]), float('inf'))
                seq2 = rota_j['sequencia'][:-1] + rota_i['sequencia'][1:]
                # Fim de i com fim de j (rota_j invertida)
                gain3 = custos_desloc.get((rota_i['sequencia'][-2], deposito), 0) + custos_desloc.get((deposito, rota_j['sequencia'][-2]), 0) - custos_desloc.get((rota_i['sequencia'][-2], rota_j['sequencia'][-2]), float('inf'))
                seq3 = rota_i['sequencia'][:-1] + rota_j['sequencia'][-2:0:-1] + [deposito]
                # Início de i com início de j (rota_i invertida)
                gain4 = custos_desloc.get((rota_i['sequencia'][1], deposito), 0) + custos_desloc.get((deposito, rota_j['sequencia'][1]), 0) - custos_desloc.get((rota_i['sequencia'][1], rota_j['sequencia'][1]), float('inf'))
                seq4 = rota_i['sequencia'][1:-1][::-1] + rota_j['sequencia'][1:]
                # Testa todas
                for gain, seq, tipo in [
                    (gain1, seq1, 'fim-inicio'),
                    (gain2, seq2, 'inicio-fim'),
                    (gain3, seq3, 'fim-fim'),
                    (gain4, seq4, 'inicio-inicio')
                ]:
                    if gain > melhor_gain:
                        melhor_gain = gain
                        melhor_nova_rota = {
                            'clientes': rota_i['clientes'] + rota_j['clientes'],
                            'demanda_total': nova_demanda,
                            'servicos': rota_i['servicos'] | rota_j['servicos'],
                            'sequencia': seq
                        }
                        melhor_i, melhor_j = i, j
                        melhor_tipo = tipo
        if melhor_nova_rota is None:
            break
        novas_rotas = []
        for k in range(len(rotas)):
            if k != melhor_i and k != melhor_j:
                novas_rotas.append(rotas[k])
        novas_rotas.append(melhor_nova_rota)
        rotas = novas_rotas
    return rotas


def floyd_warshall(nos, arestas_req, arcos_req, arestas_nr, arcos_nr):
    # Constrói lista de nós
    vertices = set()
    for v, _ in nos:
        vertices.add(v)
    def unpack(e):
        if len(e) == 3:
            return e
        elif len(e) == 2:
            return e[0], e[1], 0
        else:
            raise ValueError('Formato inesperado de aresta/arco')
    for e in arestas_req + arcos_req + arestas_nr + arcos_nr:
        (u, v), _, _ = unpack(e)
        vertices.add(u)
        vertices.add(v)
    vertices = list(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    dist = [[float('inf')] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    # Adiciona todas as arestas/arcos
    def unpack(e):
        if len(e) == 3:
            return e
        elif len(e) == 2:
            return e[0], e[1], 0
        else:
            raise ValueError('Formato inesperado de aresta/arco')
    for (u, v), c, _ in [unpack(x) for x in arestas_req + arestas_nr]:
        dist[idx[u]][idx[v]] = min(dist[idx[u]][idx[v]], c)
        dist[idx[v]][idx[u]] = min(dist[idx[v]][idx[u]], c)
    for (u, v), c, _ in [unpack(x) for x in arcos_req + arcos_nr]:
        dist[idx[u]][idx[v]] = min(dist[idx[u]][idx[v]], c)
    # Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    # Preenche custos_desloc global
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] < float('inf'):
                custos_desloc[(vertices[i], vertices[j])] = dist[i][j]


def resolver_problema(v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr):
    # Preenche matriz de deslocamento robusta
    floyd_warshall(nos, arestas_req, arcos_req, arestas_nr, arcos_nr)
    clientes = preparar_clientes(nos, arestas_req, arcos_req)
    rotas = inicializar_rotas(clientes, v0)
    rotas = juntar_rotas_iterativamente(rotas, custos_desloc, v0, Q)
    # Monta saída compatível
    rotas_finais = []
    seqs_finais = []
    for rota in rotas:
        rotas_finais.append(rota['sequencia'])
        seqs_finais.append([c['id'] for c in rota['clientes']])
    custo_d = 0
    custo_s = 0
    for rota, seq in zip(rotas_finais, seqs_finais):
        visitados = set()
        for sid in seq:
            if sid not in visitados:
                custo_s += custo_serv_dict.get(sid, 0)
                visitados.add(sid)
        for u, v in zip(rota, rota[1:]):
            if (u, v) in custos_desloc:
                custo_d += custos_desloc[(u, v)]
    return rotas_finais, seqs_finais, custo_d, custo_s