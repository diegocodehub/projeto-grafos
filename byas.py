def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    vertices = set()
    edges = set()
    arcs = set()
    required_vertices = set()
    required_edges = set()
    required_arcs = set()
    section = None

    for line in lines:
        line = line.strip()

        if line.startswith("ReN."):
            section = "ReN"
            continue
        elif line.startswith("ReE."):
            section = "ReE"
            continue
        elif line.startswith("EDGE"):
            section = "EDGE"
            continue
        elif line.startswith("ReA."):
            section = "ReA"
            continue
        elif line.startswith("ARC"):
            section = "ARC"
            continue

        if line and section:
            parts = line.split("\t")
            if section == "ReN":
                try:
                    node = int(parts[0].replace("N", ""))
                    demand = int(parts[1])
                    s_cost = int(parts[2])
                    aux = (node, (demand, s_cost))
                    required_vertices.add(aux) 
                    vertices.add(node)  
                except ValueError:
                    continue  

            elif section in ["ReE", "EDGE"]:
                try:
                    u, v = int(parts[1]), int(parts[2]) 
                    vertices.update([u, v]) #vertices q nao estavam em ReN
                    edge = (min(u, v), max(u, v)) 
                    t_cost = int(parts[3]) 
                    edges.add((edge, (t_cost))) 

                    if section == "ReE":
                        demand = int(parts[4]) 
                        s_cost = int(parts[5]) 
                        required_edges.add((edge, (t_cost, demand, s_cost)))
                except ValueError:
                    continue

            elif section in ["ReA", "ARC"]:
                try:
                    u, v = int(parts[1]), int(parts[2])
                    vertices.update([u, v]) #vertices q nao estavam em ReN
                    arc = (u, v)
                    t_cost = int(parts[3]) 
                    arcs.add((arc, (t_cost)))
                    if section == "ReA":
                        demand = int(parts[4]) 
                        s_cost = int(parts[5]) 
                        required_arcs.add((arc, (t_cost, demand, s_cost)))
                except ValueError:
                    continue

    return vertices, edges, arcs, required_vertices, required_edges, required_arcs #todos sao set


def calcula_graus(vertices, edges, arcs):
    graus = {}
    for v in vertices:
        graus[v] = [0, 0, 0]
        #[grau, grau de entrada, grau de saída]
       
    for (u, v), _ in edges:
        graus[u][0] += 1
        graus[v][0] += 1
    
    for (u, v), _ in arcs:
        graus[v][1] += 1  #grau entrada
        graus[u][2] += 1  #grau saida
        
    graus_set = tuple((v, tuple(degrees)) for v, degrees in graus.items())
    return graus_set

def imprime_graus(graus):
    #grau minimo e maximo considerando apenas arestas
    grau_min_arestas = min(g[1][0] for g in graus)
    grau_max_arestas = max(g[1][0] for g in graus)
    print(f"-   Grau minimo/maximo em relacao ao numero de arestas: {grau_min_arestas} / {grau_max_arestas}")

    #grau de entrada minimo e maximo considerando apenas arcos
    grau_entrada_min = min(g[1][1] for g in graus)
    grau_entrada_max = max(g[1][1] for g in graus)
    print(f"-   Grau de entrada minimo/maximo em relacao somente ao numero de arcos: {grau_entrada_min} / {grau_entrada_max}")

    #grau de saida minimo e maximo considerando apenas arcos
    grau_saida_min = min(g[1][2] for g in graus)
    grau_saida_max = max(g[1][2] for g in graus)
    print(f"-   Grau de saida minimo/maximo em relacao somente ao numero de arcos: {grau_saida_min} / {grau_saida_max}")

    #grau total (arestas + entrada + saida)
    grau_total_min = min(sum(g[1]) for g in graus)
    grau_total_max = max(sum(g[1]) for g in graus)
    print(f"-   Grau total minimo/maximo (grau em relacao a arestas + grau de entrada + grau de saida): {grau_total_min} / {grau_total_max}")


def calcula_densidade(NumVertices, NumEdges, NumArcs):
    edges_max=(NumVertices*(NumVertices-1))/2
    arcs_max=(NumVertices*(NumVertices-1))
    densidade = (NumEdges+NumArcs)/(edges_max+arcs_max)
    return densidade

def dijkstra(start_node, edges, arcs):
    distancias = {start_node: 0}
    predecessores = {start_node: None}
    nos_nao_visitados = set([start_node])
    
    while nos_nao_visitados:
        #current node pega o node com a menor distancia registrada/se ainda nao tem dist, ela é infinito
        current_node = min(nos_nao_visitados, key=lambda node: distancias.get(node, float('inf')))
        nos_nao_visitados.remove(current_node)
        #arestas
        for (u, v), t_cost in edges:
            if u == current_node:
                viz = v
                nova_distancia = distancias[current_node] + t_cost
            elif v == current_node:
                viz = u
                nova_distancia = distancias[current_node] + t_cost
            else:
                continue

            
            # Atualiza a distancia e o predecessor
            nova_distancia = distancias[current_node] + t_cost
            if viz not in distancias or nova_distancia < distancias[viz]:
                distancias[viz] = nova_distancia
                predecessores[viz] = current_node
                nos_nao_visitados.add(viz)
        
        #arcos
        for (u, v), t_cost in arcs:
            if u == current_node:
                viz = v
                nova_distancia = distancias[current_node] + t_cost
                if viz not in distancias or nova_distancia < distancias[viz]:
                    distancias[viz] = nova_distancia
                    predecessores[viz] = current_node
                    nos_nao_visitados.add(viz)
    return distancias, predecessores

def matriz_menores_distancias(vertices, edges, arcs):
     matriz_distancias = {}
 
     for v in vertices:
         distancias, _ = dijkstra(v, edges, arcs)  # Calcula distâncias a partir de v
         matriz_distancias[v] = {u: distancias.get(u, float('inf')) for u in vertices}  
 
     return matriz_distancias

def matriz_predecessores(vertices, edges, arcs):
    matriz_predecessores = {}
    for v in vertices:
        _, predecessores = dijkstra(v, edges, arcs)
        matriz_predecessores[v] = {u: predecessores.get(u, None) for u in vertices}  

    return matriz_predecessores

def caminho_mais_curto_com_matriz(predecessores, start_node, end_node):
    caminho = []
    current_node = end_node
    
    while current_node is not None:
        caminho.insert(0, current_node)
        current_node = predecessores[start_node].get(current_node) 
    
    return caminho

def calcula_diametro(matriz_distancias):
    return max(max(subdicionario.values()) for subdicionario in matriz_distancias.values())


def calcula_caminho_medio(numVertices, matriz_menores_distancias):
    soma = sum(sum(linha.values()) for linha in matriz_menores_distancias.values())
    divisor = numVertices*(numVertices-1)
    return soma/divisor


def calcula_intermediacao(vertices, matriz_predecessores):
    intermediacao = {v: 0 for v in vertices} 

    for u in vertices:
        for v in vertices:
            if u != v:
                caminho = caminho_mais_curto_com_matriz(matriz_predecessores, u, v)
                if caminho:
                    for vertice in caminho[1:-1]:  #Ignora primeiro e ultimo com [1:-1]
                        intermediacao[vertice] += 1

    return intermediacao

def print_metricas(vertices, edges, arcs, required_vertices, required_edges, required_arcs):
    #chama funcs metricas
    densidade = calcula_densidade(len(vertices), len(edges), len(arcs))
    matriz_distancias = matriz_menores_distancias(vertices, edges, arcs)
    matriz_pred = matriz_predecessores(vertices, edges, arcs)
    diametro = calcula_diametro(matriz_distancias)
    caminho_medio = calcula_caminho_medio(len(vertices), matriz_distancias)
    intermediacao = calcula_intermediacao(vertices, matriz_pred)
    graus = calcula_graus(vertices, edges, arcs)
    
    #print de metricas
    print(f"- Quantidade de vértices: {len(vertices)}")
    print(f"- Quantidade de arestas: {len(edges)}")
    print(f"- Quantidade de arcos: {len(arcs)}")
    print(f"- Quantidade de vértices requeridos: {len(required_vertices)}")
    print(f"- Quantidade de arestas requeridas: {len(required_edges)}")
    print(f"- Quantidade de arcos requeridos: {len(required_arcs)}")
    print(f"- Densidade do grafo: {densidade:.4f}")
    
    imprime_graus(graus)
    
    print(f"- Diâmetro do grafo: {diametro}")
    print(f"- Caminho médio: {caminho_medio:.4f}")
    print("- Intermediação de cada vértice:")
    for v, inter in intermediacao.items():
        print(f"- Vértice {v}: {inter}")


#main
print("Leia o READ.ME para colocar o arquivo em formato correto!!!")
file_path = input("Digite o caminho/nome do arquivo .dat: ")
vertices, edges, arcs, required_vertices, required_edges, required_arcs = read_file(file_path)
print_metricas(vertices, edges, arcs, required_vertices, required_edges, required_arcs)




#TODO
# 1. Quantidade de vértices; OK
# 2. Quantidade de arestas; OK
# 3. Quantidade de arcos; OK
# 4. Quantidade de vértices requeridos; OK
# 5. Quantidade de arestas requeridas; OK
# 6. Quantidade de arcos requeridos; OK
# 7. Densidade do grafo (order strength) OK
# 8. Componentes conectados; OK
# 9. Grau mínimo dos vértices; OK
# 10. Grau máximo dos vértices; OK
# 11. Intermediação - Mede a frequência com que um nó aparece nos caminhos mais curtos OK;
# 12. Caminho médio OK;
# 13. Diâmetro OK;
#
# Importante: Muitas dessas métricas utilizam os resultados da matriz de caminhos mais curtos de múltiplas fontes.
# Assim, como um dos produtos da Etapa 1, é necessário desenvolver o algoritmo que gera tal matriz,
# assim como a matriz de predecessores.