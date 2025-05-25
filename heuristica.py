import random
from collections import defaultdict
import heapq

def extrair_tarefas(nos, arestas_req, arcos_req):
    tarefas = []
    id_servico = 1
    for v, q in nos:
        tarefas.append({'tipo': 'vertice', 'id': id_servico, 'origem': v, 'destino': v, 'demanda': q, 'custo_servico': 0, 't_cost': 0})
        id_servico += 1
    for (u, v), c, q in arestas_req:
        tarefas.append({'tipo': 'edge', 'id': id_servico, 'origem': u, 'destino': v, 'demanda': q, 'custo_servico': c, 't_cost': c})
        id_servico += 1
    for (u, v), c, q in arcos_req:
        tarefas.append({'tipo': 'arc', 'id': id_servico, 'origem': u, 'destino': v, 'demanda': q, 'custo_servico': c, 't_cost': c})
        id_servico += 1
    return tarefas

def construir_grafo(nos, arestas_req, arcos_req, arestas_nr, arcos_nr):
    grafo = defaultdict(list)
    for v, _ in nos:
        grafo[v] = []
    for (u, v), c, *_ in arestas_req + arestas_nr:
        grafo[u].append((v, c))
        grafo[v].append((u, c))
    for (u, v), c, *_ in arcos_req + arcos_nr:
        grafo[u].append((v, c))
    return grafo

def dijkstra_pred(grafo, origem):
    dist = defaultdict(lambda: float('inf'))
    pred = {}
    dist[origem] = 0
    heap = [(0, origem)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, custo in grafo[u]:
            if dist[v] > d + custo:
                dist[v] = d + custo
                pred[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist, pred

def caminho_mais_curto(pred, origem, destino):
    if origem == destino:
        return [origem]
    caminho = [destino]
    atual = destino
    while atual != origem:
        atual = pred.get(atual)
        if atual is None:
            return []
        caminho.append(atual)
    return list(reversed(caminho))

def matriz_menores_distancias(nos, arestas_req, arcos_req, arestas_nr, arcos_nr):
    grafo = construir_grafo(nos, arestas_req, arcos_req, arestas_nr, arcos_nr)
    vertices = set(grafo.keys())
    matriz = {u: {v: float('inf') for v in vertices} for u in vertices}
    for u in vertices:
        matriz[u][u] = 0
    for u in vertices:
        dist, _ = dijkstra_pred(grafo, u)
        for v in vertices:
            matriz[u][v] = dist[v]
    return matriz

def calcula_custos_entre_tarefas(tarefas, matriz_distancias):
    custos = {}
    for i, t1 in enumerate(tarefas):
        for j, t2 in enumerate(tarefas):
            if i == j:
                continue
            origem_t1 = t1['destino'] if t1['tipo'] != 'vertice' else t1['origem']
            destino_t2 = t2['origem']
            custo = matriz_distancias[origem_t1][destino_t2] + t1['custo_servico'] + t2['custo_servico']
            custos[(i, j)] = custo
    return custos

def construir_rota_completa(tarefas, tarefa_indices, depot_node, matriz_pred):
    rota = [depot_node]
    for i, idx in enumerate(tarefa_indices):
        tarefa = tarefas[idx]
        origem = tarefa['origem']
        if i == 0:
            rota += caminho_mais_curto(matriz_pred[rota[-1]], rota[-1], origem)[1:]
        else:
            anterior = tarefas[tarefa_indices[i - 1]]
            ultimo = anterior['destino'] if anterior['tipo'] != 'vertice' else anterior['origem']
            rota += caminho_mais_curto(matriz_pred[ultimo], ultimo, origem)[1:]
        if tarefa['tipo'] == 'vertice':
            pass
        else:
            rota.append(tarefa['destino'])
    ultimo = tarefas[tarefa_indices[-1]]
    fim = ultimo['destino'] if ultimo['tipo'] != 'vertice' else ultimo['origem']
    rota += caminho_mais_curto(matriz_pred[fim], fim, depot_node)[1:]
    return rota

def inicializa_rotas(tarefas, depot_node, capacity, matriz_pred):
    rotas = []
    for idx, tarefa in enumerate(tarefas):
        if tarefa['demanda'] > capacity:
            continue
        rota_completa = construir_rota_completa(tarefas, [idx], depot_node, matriz_pred)
        rotas.append({'tarefas': [idx], 'demanda': tarefa['demanda'], 'rota_completa': rota_completa})
    return rotas

def pode_fundir_rotas(rota_i, rota_j, capacidade_max):
    return (rota_i['demanda'] + rota_j['demanda']) <= capacidade_max

def funde_rotas(rota_i, rota_j, tarefas, depot_node, matriz_pred):
    nova_tarefas = rota_i['tarefas'] + rota_j['tarefas']
    nova_demanda = rota_i['demanda'] + rota_j['demanda']
    nova_rota = construir_rota_completa(tarefas, nova_tarefas, depot_node, matriz_pred)
    return {'tarefas': nova_tarefas, 'demanda': nova_demanda, 'rota_completa': nova_rota}

def calcula_savings(tarefas, custos_entre_tarefas, matriz_distancias, deposito, capacidade_max):
    savings = []
    for i, t1 in enumerate(tarefas):
        for j, t2 in enumerate(tarefas):
            if i >= j:
                continue
            if (t1['demanda'] + t2['demanda']) > capacidade_max:
                continue
            custo_i0 = matriz_distancias[deposito][t1['origem']]
            custo_0j = matriz_distancias[t2['destino']][deposito] if t2['tipo'] != 'vertice' else matriz_distancias[t2['origem']][deposito]
            saving = custo_i0 + custo_0j - custos_entre_tarefas[(i, j)]
            savings.append(((i, j), saving))
    return savings

def ordenar_savings(savings, rng=None):
    if rng is not None:
        rng.shuffle(savings)
    else:
        savings = sorted(savings, key=lambda x: x[1], reverse=True)
    return savings

def aplica_savings(rotas, savings, capacidade_max, tarefas, depot_node, matriz_pred):
    for (i, j), _ in savings:
        rota_i = next((r for r in rotas if r['tarefas'] and r['tarefas'][-1] == i), None)
        rota_j = next((r for r in rotas if r['tarefas'] and r['tarefas'][0] == j), None)
        if rota_i and rota_j and rota_i != rota_j:
            if pode_fundir_rotas(rota_i, rota_j, capacidade_max):
                nova_rota = funde_rotas(rota_i, rota_j, tarefas, depot_node, matriz_pred)
                rotas.remove(rota_i)
                rotas.remove(rota_j)
                rotas.append(nova_rota)
    return rotas

def grasp_2opt_carp(v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr, iteracoes=1, max_iter_2opt=0, alpha=0.3):
    tarefas = extrair_tarefas(nos, arestas_req, arcos_req)
    grafo = construir_grafo(nos, arestas_req, arcos_req, arestas_nr, arcos_nr)
    matriz_distancias = matriz_menores_distancias(nos, arestas_req, arcos_req, arestas_nr, arcos_nr)
    matriz_pred = {u: dijkstra_pred(grafo, u)[1] for u in grafo}
    custos_entre_tarefas = calcula_custos_entre_tarefas(tarefas, matriz_distancias)
    rotas = inicializa_rotas(tarefas, v0, Q, matriz_pred)
    savings = calcula_savings(tarefas, custos_entre_tarefas, matriz_distancias, v0, Q)
    savings_ordenados = ordenar_savings(savings, rng=random)
    rotas = aplica_savings(rotas, savings_ordenados, Q, tarefas, v0, matriz_pred)
    # Opcional: 2-opt ou outra otimização pode ser aplicada aqui
    return rotas, tarefas

def custo_rota_especifica(rota, tarefas, matriz_distancias):
    custo_total = 0
    for tarefa_id in rota['tarefas']:
        tarefa = tarefas[tarefa_id]
        custo_total += tarefa['custo_servico']
    rota_completa = rota['rota_completa']
    transporte_total = 0
    for i in range(len(rota_completa) - 1):
        origem = rota_completa[i]
        destino = rota_completa[i + 1]
        transporte_total += matriz_distancias[origem][destino]
    transporte_das_tarefas = 0
    for tarefa_id in rota['tarefas']:
        tarefa = tarefas[tarefa_id]
        transporte_das_tarefas += tarefa['t_cost']
    transporte_total -= transporte_das_tarefas
    custo_total += transporte_total
    return custo_total

def custo_rota_real(caminho_real, servicos_map, custos_desloc, custo_serv_dict):
    desloc_total = 0
    desloc_tarefas = 0
    custo_servicos = 0
    visitados = set()
    for i in range(len(caminho_real)-1):
        u, v = caminho_real[i], caminho_real[i+1]
        desloc = custos_desloc.get((u, v), 0)
        desloc_total += desloc
        if (u, v) in servicos_map and (u, v) not in visitados:
            id_serv, tipo = servicos_map[(u, v)]
            custo_servicos += custo_serv_dict.get(id_serv, 0)
            desloc_tarefas += desloc
            visitados.add((u, v))
        elif (v, u) in servicos_map and (v, u) not in visitados and servicos_map[(v, u)][1] == 'e':
            id_serv, tipo = servicos_map[(v, u)]
            custo_servicos += custo_serv_dict.get(id_serv, 0)
            desloc_tarefas += custos_desloc.get((v, u), 0)
            visitados.add((v, u))
        elif (v, v) in servicos_map and (v, v) not in visitados:
            id_serv, tipo = servicos_map[(v, v)]
            custo_servicos += custo_serv_dict.get(id_serv, 0)
            visitados.add((v, v))
    custo_rota = custo_servicos + (desloc_total - desloc_tarefas)
    return custo_rota