import numpy

def ler_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    qtdVeiculos = int(linhas[2].split()[-1])
    capacidade = int(linhas[3].split()[-1])
    deposito = int(linhas[4].split()[-1])
    qtdVertices = int(linhas[5].split()[-1])
    qtdArestas = int(linhas[6].split()[-1])
    qtdArcos = int(linhas[7].split()[-1])
    qtdVerticesReq = int(linhas[8].split()[-1])
    qtdArestasReq = int(linhas[9].split()[-1])
    qtdArcosReq = int(linhas[10].split()[-1])

    grafo = numpy.full((qtdVertices + 1, qtdVertices + 1), numpy.inf)
    numpy.fill_diagonal(grafo, 0)

    i = 12
    verticesReq = {}

    while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("ReE."):
        partes = linhas[i].split()
        if partes[0].startswith("N"):
            v = int(partes[0][1:])
            demanda = int(partes[1])
            custoServico = int(partes[2])
            verticesReq[v] = (demanda, custoServico)
        i += 1

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
            grafo[origem][destino] = custoTransporte
            grafo[destino][origem] = custoTransporte
            arestasReq.append((origem, destino, custoTransporte, demanda, custoServico))
            arestas.append((origem, destino, custoTransporte))
        i += 1

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
            grafo[origem][destino] = custoTransporte
            arcosReq.append((origem, destino, custoTransporte, demanda, custoServico))
            arcos.append((origem, destino, custoTransporte))
        i += 1

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
    return a / (n * (n - 1)) if n > 1 else 0

def componentes_conectados(grafo):
    n = grafo.shape[0]
    visitado = [False] * n
    componentes = 0

    def dfs(v):
        visitado[v] = True
        for u in range(n):
            if (grafo[v][u] < numpy.inf or grafo[u][v] < numpy.inf) and not visitado[u]:
                dfs(u)

    for v in range(n):
        if not visitado[v]:
            componentes += 1
            dfs(v)

    return componentes

def graus_vertices(dados):
    grafo = dados["grafo"]
    n = grafo.shape[0]
    graus = []
    for v in range(n):
        grau_saida = sum(1 for u in range(n) if grafo[v][u] < numpy.inf and u != v)
        grau_entrada = sum(1 for u in range(n) if grafo[u][v] < numpy.inf and u != v)
        graus.append((v, grau_entrada, grau_saida))
    return graus

def fw(grafo):
    n = grafo.shape[0]
    distancia = grafo.copy()
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if distancia[i][j] > distancia[i][k] + distancia[k][j]:
                    distancia[i][j] = distancia[i][k] + distancia[k][j]
    return distancia

def caminho_medio(grafo):
    d = fw(grafo)
    n = grafo.shape[0]
    soma = 0
    cont = 0
    for i in range(n):
        for j in range(n):
            if i != j and d[i][j] < numpy.inf:
                soma += d[i][j]
                cont += 1
    return soma / cont if cont > 0 else 0

def diametro(grafo):
    d = fw(grafo)
    n = grafo.shape[0]
    return max(d[i][j] for i in range(n) for j in range(n) if d[i][j] < numpy.inf)

def intermediacao(grafo):
    n = grafo.shape[0]
    centralidade = [0] * n
    for s in range(n):
        stack = []
        pred = [[] for _ in range(n)]
        sigma = [0] * n
        dist = [-1] * n
        sigma[s] = 1
        dist[s] = 0
        queue = [s]
        while queue:
            v = queue.pop(0)
            stack.append(v)
            for w in range(n):
                if grafo[v][w] < numpy.inf:
                    if dist[w] < 0:
                        queue.append(w)
                        dist[w] = dist[v] + 1
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)
        delta = [0] * n
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                centralidade[w] += delta[w]
    return centralidade

def main():
    nome_arquivo = input("Digite o nome do arquivo .dat: ")
    dados = ler_arquivo(nome_arquivo)
    grafo = dados["grafo"]

    print("\n--- Estatísticas básicas ---")
    for k, v in estatisticas_basicas(dados).items():
        print(f"{k}: {v}")

    print(f"\nDensidade: {densidade(dados):.4f}")
    print(f"Componentes conectados: {componentes_conectados(grafo)}")

    print("\n--- Graus dos vértices ---")
    for v, g_in, g_out in graus_vertices(dados):
        print(f"Vértice {v}: Entrada = {g_in}, Saída = {g_out}")

    print(f"\nCaminho médio: {caminho_medio(grafo):.2f}")
    print(f"Diâmetro: {diametro(grafo):.2f}")

    print("\n--- Intermediação ---")
    for i, c in enumerate(intermediacao(grafo)):
        print(f"Vértice {i}: {c:.2f}")

if __name__ == "__main__":
    main()