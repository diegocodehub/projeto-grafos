#-----------------------------------------#
# Projeto Prático de Grafos - Etapa 1     #
# Grupo:                                  #
# Caio Bueno Finocchio Martins (202410377)#
# Diego Alves de Oliveira (202410370)     #
#-----------------------------------------#

import numpy as np
import heapq

# Declarando variável global grafo
global_grafo = None

# Função para ler o arquivo .dat e extrair os dados relevantes
def ler_arquivo(nome_arquivo):

    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        qtd_veiculos = int(linhas[2].split()[-1])
        capacidade = int(linhas[3].split()[-1])
        deposito = int(linhas[4].split()[-1])
        qtd_vertices = int(linhas[5].split()[-1])
        qtd_arestas = int(linhas[6].split()[-1])
        qtd_arcos = int(linhas[7].split()[-1])
        qtd_vertices_req = int(linhas[8].split()[-1])
        qtd_arestas_req = int(linhas[9].split()[-1])
        qtd_arcos_req = int(linhas[10].split()[-1])

        grafo = np.full((qtd_vertices + 1, qtd_vertices + 1), np.inf)
        np.fill_diagonal(grafo, 0)

        i = 12
        
        # Adiciona os vértices requeridos ao grafo
        vertices_req = {}
        
        while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("ReE."):
            partes = linhas[i].split()
            if partes[0].startswith("N"):
                v = int(partes[0][1:])
                demanda = int(partes[1])
                custo_servico = int(partes[2])
                vertices_req[v] = (demanda, custo_servico)
            i += 1

        # Adiciona os vértices requeridos ao grafo
        while i < len(linhas) and not linhas[i].startswith("ReE."):
            i += 1
        i += 1

        arestas_req = []
        arestas = []
        while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("EDGE"):
            partes = linhas[i].split()
            if partes[0].startswith("E"):
                origem, destino = map(int, [partes[1], partes[2]])
                custo_transporte = int(partes[3])
                demanda = int(partes[4])
                custo_servico = int(partes[5])
                grafo[origem][destino] = custo_transporte
                grafo[destino][origem] = custo_transporte
                arestas_req.append((origem, destino, custo_transporte, demanda, custo_servico))
                arestas.append((origem, destino, custo_transporte))
            i += 1

        # Adiciona as arestas bidirecionais ao grafo
        while i < len(linhas) and not linhas[i].startswith("EDGE"):
            i += 1
        i += 1

        while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("ReA."):
            partes = linhas[i].split()
            if partes[0].startswith("NrE"):
                origem, destino = map(int, [partes[1], partes[2]])
                custo_transporte = int(partes[3])
                grafo[origem][destino] = custo_transporte
                grafo[destino][origem] = custo_transporte
                arestas.append((origem, destino, custo_transporte))
            i += 1

        # Adiciona os arcos direcionais ao grafo
        while i < len(linhas) and not linhas[i].startswith("ReA."):
            i += 1
        i += 1

        arcos_req = []
        arcos = []
        while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith("ARC"):
            partes = linhas[i].split()
            if partes[0].startswith("A"):
                origem, destino = map(int, [partes[1], partes[2]])
                custo_transporte = int(partes[3])
                demanda = int(partes[4])
                custo_servico = int(partes[5])
                grafo[origem][destino] = custo_transporte
                arcos_req.append((origem, destino, custo_transporte, demanda, custo_servico))
                arcos.append((origem, destino, custo_transporte))
            i += 1

        # Adiciona os arcos bidirecionais ao grafo
        while i < len(linhas) and not linhas[i].startswith("ARC"):
            i += 1
        i += 1

        while i < len(linhas) and linhas[i].strip():
            partes = linhas[i].split()
            if partes[0].startswith("NrA"):
                origem, destino = map(int, [partes[1], partes[2]])
                custo_transporte = int(partes[3])
                grafo[origem][destino] = custo_transporte
                arcos.append((origem, destino, custo_transporte))
            i += 1

        return {
            "qtd_veiculos": qtd_veiculos,
            "capacidade": capacidade,
            "deposito": deposito,
            "qtd_vertices": qtd_vertices,
            "qtd_arestas": qtd_arestas,
            "qtd_arcos": qtd_arcos,
            "qtd_vertices_req": qtd_vertices_req,
            "qtd_arestas_req": qtd_arestas_req,
            "qtd_arcos_req": qtd_arcos_req,
            "vertices_req": vertices_req,
            "arestas_req": arestas_req,
            "arestas": arestas,
            "arcos_req": arcos_req,
            "arcos": arcos,
            "grafo": grafo
        }
    except Exception as e:
        raise ValueError(f"Erro ao processar o arquivo: {str(e)}")

# Função para calcular a densidade do grafo
def densidade(qtd_vertices, qtd_arestas, qtd_arcos):
    max_ligacoes_arestas = (qtd_vertices * (qtd_vertices - 1)) / 2
    max_ligacoes_arcos = (qtd_vertices * (qtd_vertices - 1))
    total_ligacoes = max_ligacoes_arestas + max_ligacoes_arcos
    return (qtd_arestas + qtd_arcos) / total_ligacoes

# Função para calcular os graus dos vértices
def calcula_graus(dados):
    qtd_vertices = dados["qtd_vertices"]
    grau_arestas = [0] * (qtd_vertices + 1)
    grau_entrada = [0] * (qtd_vertices + 1)
    grau_saida = [0] * (qtd_vertices + 1)

    for origem, destino, _ in dados["arestas"]:
        grau_arestas[origem] += 1
        grau_arestas[destino] += 1

    for origem, destino, _ in dados["arcos"]:
        grau_saida[origem] += 1
        grau_entrada[destino] += 1

    resultado = []
    for v in range(1, qtd_vertices + 1):
        total = grau_arestas[v] + grau_entrada[v] + grau_saida[v]
        resultado.append((v, grau_arestas[v], grau_entrada[v], grau_saida[v], total))

    return resultado

# Implementação do algoritmo de Dijkstra
def dijkstra(grafo, inicio):

    n = grafo.shape[0]
    distancias = {v: float('inf') for v in range(n)}
    predecessores = {v: -1 for v in range(n)}
    distancias[inicio] = 0
    
    heap = []
    heapq.heappush(heap, (0, inicio))
    
    visitados = set()
    
    while heap:
        dist_atual, vertice_atual = heapq.heappop(heap)
        
        if vertice_atual in visitados:
            continue
            
        visitados.add(vertice_atual)
        
        for vizinho in range(n):
            if grafo[vertice_atual][vizinho] < float('inf'):
                distancia = dist_atual + grafo[vertice_atual][vizinho]
                
                if distancia < distancias[vizinho]:
                    distancias[vizinho] = distancia
                    predecessores[vizinho] = vertice_atual
                    heapq.heappush(heap, (distancia, vizinho))
    
    return distancias, predecessores

# Função para calcular todas as distâncias usando Dijkstra
def calcular_todas_distancias_dijkstra(grafo):
  
    n = grafo.shape[0]
    distancias = np.full((n, n), np.inf)
    predecessores = np.full((n, n), -1)
    
    for i in range(n):
        dist, pred = dijkstra(grafo, i)
        for j in range(n):
            distancias[i][j] = dist[j]
            predecessores[i][j] = pred[j]
    
    np.fill_diagonal(distancias, 0)
    return distancias, predecessores

# Função de Floyd-Warshall para comparação
def floyd_warshall(grafo):
    n = grafo.shape[0]
    distancia = grafo.copy()
    predecessores = np.full((n, n), -1)

    for i in range(n):
        for j in range(n):
            if i != j and grafo[i][j] < np.inf:
                predecessores[i][j] = i

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if distancia[i][j] > distancia[i][k] + distancia[k][j]:
                    distancia[i][j] = distancia[i][k] + distancia[k][j]
                    predecessores[i][j] = predecessores[k][j]

    return distancia, predecessores

# Função para calcular o caminho médio entre todos os pares de vértices
def caminho_medio(distancias):
    n = distancias.shape[0]
    soma = 0
    cont = 0
    for i in range(1, n):
        for j in range(1, n):
            if i != j and distancias[i][j] < np.inf:
                soma += distancias[i][j]
                cont += 1
    return soma / cont if cont > 0 else 0

# Função para calcular o diâmetro do grafo
def diametro(distancias):
    n = distancias.shape[0]
    max_dist = 0
    for i in range(1, n):
        for j in range(1, n):
            if i != j and distancias[i][j] < np.inf:
                max_dist = max(max_dist, distancias[i][j])
    return int(max_dist)

# Função para reconstruir o caminho mais curto
def reconstruir_caminho(predecessores, inicio, fim):
    caminho = []
    atual = fim
    
    while atual != -1 and atual != inicio and atual in predecessores:
        caminho.insert(0, atual)
        atual = predecessores[atual]
    
    if atual == inicio:
        caminho.insert(0, inicio)
        return caminho
    return None

# Função para calcular a intermediação de cada vértice usando Dijkstra
def calcula_intermediacao(vertices, grafo):
    intermediacao = {v: 0 for v in vertices}
    
    for u in vertices:
        distancias, predecessores = dijkstra(grafo, u)
        for v in vertices:
            if u != v:
                caminho = reconstruir_caminho(predecessores, u, v)
                if caminho:
                    for vertice in caminho[1:-1]:  # Ignora o primeiro e o último vértice
                        intermediacao[vertice] += 1
    
    return intermediacao

def carregar_grafo(nome_arquivo):
    dados = ler_arquivo(nome_arquivo)
    return dados["grafo"], dados

def main():
    try:
        nome_arquivo = input("Digite o nome do arquivo .dat (ex: nome_arquivo.dat): ")
        dados = ler_arquivo(nome_arquivo)
        grafo = dados["grafo"]

        # print("")
        # print(f"- ESTATÍSTICAS BÁSICAS DO GRAFO:")
        # print(f"- Quantidade de vértices: {dados['qtd_vertices']}")
        # print(f"- Quantidade de arestas: {dados['qtd_arestas']}")
        # print(f"- Quantidade de arcos: {dados['qtd_arcos']}")
        # print(f"- Quantidade de vértices requeridos: {dados['qtd_vertices_req']}")
        # print(f"- Quantidade de arestas requeridas: {dados['qtd_arestas_req']}")
        # print(f"- Quantidade de arcos requeridos: {dados['qtd_arcos_req']}")
        # print(f"- Densidade do grafo: {densidade(dados['qtd_vertices'], dados['qtd_arestas'], dados['qtd_arcos']):.4f}")

        # Cálculo dos graus por vértice
        graus = calcula_graus(dados)
        graus = [g for g in graus if g[0] != 0]
        grau_total_list = [g[4] for g in graus]

        # print(f"- Grau total mínimo: {min(grau_total_list)}")
        # print(f"- Grau total máximo: {max(grau_total_list)}")

        # Escolhe o algoritmo baseado na densidade do grafo
        dens = densidade(dados['qtd_vertices'], dados['qtd_arestas'], dados['qtd_arcos'])
        if dens > 0.5:                                                                    # Grafo denso - Floyd-Warshall é mais eficiente
            distancias, predecessores = floyd_warshall(grafo)
        else:                                                                             # Grafo esparso - Dijkstra é mais eficiente
            distancias, predecessores = calcular_todas_distancias_dijkstra(grafo)

        # print(f"- Caminho médio: {caminho_medio(distancias):.4f}")
        # print(f"- Diâmetro do grafo: {diametro(distancias)}")

        # Exportação das estátisticas para estatisticas.csv para melhor vizualização
        with open("estatisticas.csv", "w", encoding="utf-8") as arq:
            arq.write(f"\n")
            arq.write(f"MÉTRICA,VALOR\n")
            arq.write(f"Quantidade de vértices,{dados['qtd_vertices']}\n")
            arq.write(f"Quantidade de arestas,{dados['qtd_arestas']}\n")
            arq.write(f"Quantidade de arcos,{dados['qtd_arcos']}\n")
            arq.write(f"Quantidade de vértices requeridos,{dados['qtd_vertices_req']}\n")
            arq.write(f"Quantidade de arestas requeridas,{dados['qtd_arestas_req']}\n")
            arq.write(f"Quantidade de arcos requeridos,{dados['qtd_arcos_req']}\n")
            arq.write(f"Densidade do grafo,{densidade(dados['qtd_vertices'], dados['qtd_arestas'], dados['qtd_arcos']):.4f}\n")
            arq.write(f"Grau total mínimo,{min(grau_total_list)}\n")
            arq.write(f"Grau total máximo,{max(grau_total_list)}\n")
            arq.write(f"Caminho médio,{caminho_medio(distancias):.4f}\n")
            arq.write(f"Diâmetro do grafo,{diametro(distancias)}\n")

        # Exportação da intermediação para intermediacao.csv para melhor vizualização
        with open("intermediacao.csv", "w", encoding="utf-8") as arq:
            vertices = list(range(1, dados["qtd_vertices"] + 1))
            intermed = calcula_intermediacao(vertices, grafo)
            arq.write(f"VÉRTICE,QUANTIDADE\n")
            for vertice in sorted(intermed.keys()):
                arq.write(f"Vértice {vertice},{intermed[vertice]}\n")

        # print("")
        # print("- INTERMEDIAÇÃO DOS VÉRTICES:")
        # vertices = list(range(1, dados["qtd_vertices"] + 1))
        # intermed = calcula_intermediacao(vertices, grafo)
        # for vertice in sorted(intermed.keys()):
        # print(f"- Vértice {vertice}: {intermed[vertice]}")

        # Atualizando variável global grafo (para visualização)
        global global_grafo
        global_grafo = grafo

    except ValueError as e:
        print(f"Erro: {str(e)}")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main()
