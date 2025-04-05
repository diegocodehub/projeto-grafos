import numpy

def ler_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    # Informações gerais
    qtdVeiculos = int(linhas[2].split()[-1])
    capacidade = int(linhas[3].split()[-1])
    deposito = int(linhas[4].split()[-1])
    qtdVertices = int(linhas[5].split()[-1])
    qtdArestas = int(linhas[6].split()[-1])
    qtdArcos = int(linhas[7].split()[-1])
    qtdVerticesReq = int(linhas[8].split()[-1])
    qtdArestasReq = int(linhas[9].split()[-1])
    qtdArcosReq = int(linhas[10].split()[-1])
    
    # Criar matriz de adjacência inicial com infinito
    grafo = numpy.full((qtdVertices + 1, qtdVertices + 1), numpy.inf)
    numpy.fill_diagonal(grafo, 0)
    
    # Ler ReN
    i = 12  # Linha onde começa a tabela "ReN."
    verticesReq = {}

    while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("ReE."):
        partes = linhas[i].split()
        if partes[0].startswith("N"):
            v = int(partes[0][1:])
            demanda = int(partes[1])
            custoServico = int(partes[2])
            verticesReq[v] = (demanda, custoServico)
        i += 1
    
    # Ler ReE
    while not linhas[i].startswith("ReE."):
        i += 1
    i += 1  

    arestasReq = []
    arestas = []
    while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("EDGE"):
        partes = linhas[i].split()
        if partes[0].startswith("E"):
            origem, destino = map(int, [partes[1], partes[2]])
            custoTransporte = int(partes[3])
            demanda = int(partes[4])
            custoServico = int(partes[5])
            grafo[origem][destino] = custoTransporte # Bidirecionado
            grafo[destino][origem] = custoTransporte
            arestasReq.append((origem, destino, custoTransporte, demanda, custoServico))
            arestas.append((origem, destino, custoTransporte))
        i += 1
    
    # Ler EDGE
    while not linhas[i].startswith("EDGE"):
        i += 1
    i += 1  

    while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("ReA."):
        partes = linhas[i].split()
        if partes[0].startswith("NrE"):
            origem, destino = map(int, [partes[1], partes[2]])
            custoTransporte = int(partes[3])
            grafo[origem][destino] = custoTransporte
            grafo[destino][origem] = custoTransporte
            arestas.append((origem, destino, custoTransporte))
        i += 1
    

    # Ler ReA
    while not linhas[i].startswith("ReA."):
        i += 1
    i += 1
    arcosReq = []
    arcos = []
    while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("ARC"):
        partes = linhas[i].split()
        if partes[0].startswith("A"):
            origem, destino = map(int, [partes[1], partes[2]])
            custoTransporte = int(partes[3])
            demanda = int(partes[4])
            custoServico = int(partes[5])
            grafo[origem][destino] = custoTransporte  # Direcionado
            arcosReq.append((origem, destino, custoTransporte, demanda, custoServico))
            arcos.append((origem, destino, custoTransporte))
        i += 1
    
    # Ler ARC
    while not linhas[i].startswith("ARC"):
        i += 1
    i += 1  

    while i < len(linhas) and linhas[i].strip():
        partes = linhas[i].split()
        if partes[0].startswith("NrA."):
            origem, destino = map(int, [partes[1], partes[2]])
            custoTransporte = int(partes[3])
            grafo[origem][destino] = custoTransporte
            arcos.append((origem, destino, custoTransporte))
        i += 1

    return {
        "qtdVeiculos": qtdVeiculos,
        "capacidade": capacidade,
        "deposito": deposito,
        "qtdVertices": qtdVertices,
        "qtdArestas": qtdArestas,
        "qtdArcos": qtdArcos,
        "qtdVerticesReq": qtdVerticesReq,
        "qtdArestasReq": qtdArestasReq,
        "qtdArcosReq": qtdArcosReq,
        "verticesReq": verticesReq,
        "arestasReq": arestasReq,
        "arestas": arestas,
        "arcosReq": arcosReq,
        "arcos": arcos,
        "grafo": grafo
    }

def estatisticas_basicas(dados):
    return {
        "qtd_vertices": dados["qtdVertices"],
        "qtd_arestas": dados["qtdArestas"],
        "qtd_arcos": dados["qtdArcos"],
        "qtd_vertices_req": dados["qtdVerticesReq"],
        "qtd_arestas_req": dados["qtdArestasReq"],
        "qtd_arcos_req": dados["qtdArcosReq"]
    }

def densidade(dados):
    n = dados["qtdVertices"]
    a = len(dados["arestas"]) + len(dados["arcos"])
    if n > 1:
        return a / (n * (n - 1))
    else: return 0

def componentes_conectados(grafo):
    n = grafo.shape[0]
    visitado = [False] * v
    componentesConectados = 0

    # Depth-First Search
    def dfs(v):
        visitado[v] = True
        for u in range(n):
            # Considera o grafo como não-direcionado
            if grafo[v][u] < numpy.inf or grafo[u][v] < numpy.inf and not visitado[u]:
                dfs(u)

    for v in range(n):
        if not visitado[v]:
            componentesConectados += 1
            dfs(v)

    return componentesConectados

def graus_vertices(dados):
    return

# Floyd-Warshall 
def fw(grafo):
    n = grafo.shape[0]
    distancia = grafo.copy()
    predecessores = numpy.full((n, n), -1)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if distancia[i][j] > distancia[i][k] + distancia[k][j]:
                    distancia[i][j] = distancia[i][k] + distancia[k][j]
                    predecessores[i][j] = predecessores[k][j]

    return distancia, predecessores

def intermediacao():

def caminho_medio():

def diametro():
