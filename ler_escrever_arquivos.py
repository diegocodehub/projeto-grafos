# Funções para leitura e escrita de arquivos do projeto CARP
import os
import csv
import re

def ler_instancia(caminho):
    """
    Lê um arquivo de instância .dat do CARP e retorna os dados estruturados.
    Parâmetros:
        caminho (str): Caminho do arquivo .dat
    Retorna:
        tuple: (deposito, capacidade, arestas_req, arcos_req, nos, arestas_nr, arcos_nr)
    """
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = [l.rstrip() for l in f if l.strip()]
        capacidade   = int(linhas[3].split()[-1])
        deposito     = int(linhas[4].split()[-1])
        qtd_v_req    = int(linhas[8].split()[-1])
        qtd_e_req    = int(linhas[9].split()[-1])
        qtd_a_req    = int(linhas[10].split()[-1])
        i = 12
        nos = []
        for _ in range(qtd_v_req):
            partes = linhas[i].split()
            v = int(partes[0][1:]); q = int(partes[1])
            nos.append((v, q)); i += 1
        while not linhas[i].startswith('ReE.'):
            i += 1
        i += 1
        arestas_req = []
        for _ in range(qtd_e_req):
            p = linhas[i].split()
            o, d, c, qv = map(int, p[1:5])
            arestas_req.append(((o, d), c, qv)); i += 1
        while not linhas[i].startswith('EDGE'):
            i += 1
        i += 1
        arestas_nr = []
        while i < len(linhas) and linhas[i] and not linhas[i].startswith('ReA.'):
            p = linhas[i].split()
            if len(p) >= 4:
                o, d, c = map(int, p[1:4])
                arestas_nr.append(((o, d), c))
            i += 1
        while not linhas[i].startswith('ReA.'):
            i += 1
        i += 1
        arcos_req = []
        for _ in range(qtd_a_req):
            p = linhas[i].split()
            o, d, c, qv = map(int, p[1:5])
            arcos_req.append(((o, d), c, qv)); i += 1
        while not linhas[i].startswith('ARC'):
            i += 1
        i += 1
        arcos_nr = []
        while i < len(linhas):
            p = linhas[i].split()
            if len(p) >= 4 and p[0].startswith('NrA'):
                o, d, c = map(int, p[1:4])
                arcos_nr.append(((o, d), c))
            i += 1
        return deposito, capacidade, arestas_req, arcos_req, nos, arestas_nr, arcos_nr
    except Exception as e:
        raise RuntimeError(f"Erro ao ler instância: {e}")

def ler_reference_values(caminho_csv, nome_base):
    """
    Lê o arquivo de valores de referência e retorna clocks e clocks_melhor_sol para a instância.
    Parâmetros:
        caminho_csv (str): Caminho do arquivo reference_values.csv
        nome_base (str): Nome base da instância
    Retorna:
        tuple: (clocks, clocks_melhor_sol)
    """
    try:
        with open(caminho_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row and row[0].strip() == nome_base:
                    return int(row[3]), int(row[4])
    except Exception as e:
        raise RuntimeError(f"Erro ao ler reference_values.csv: {e}")
    return -1, -1

def salvar_solucao(saida, custo_total, num_rotas, clock_melhor_sol, ciclos_estimados, rotas, seq_ids_por_rota, demanda_rota, custo_rota, detalhes_rotas):
    """
    Salva a solução gerada no formato esperado.
    Parâmetros:
        saida (str): Caminho do arquivo de saída
        custo_total (float): Custo total da solução
        num_rotas (int): Número de rotas
        clock_melhor_sol (int): Clock da melhor solução de referência
        ciclos_estimados (int): Ciclos estimados
        rotas, seq_ids_por_rota, demanda_rota, custo_rota, detalhes_rotas: detalhes das rotas
    """
    with open(saida, 'w', encoding='utf-8') as f:
        f.write(f"{custo_total}\n")
        f.write(f"{num_rotas}\n")
        f.write(f"{clock_melhor_sol}\n")
        f.write(f"{ciclos_estimados}\n")
        for rid, (detalhes) in enumerate(detalhes_rotas, start=1):
            f.write(detalhes + "\n")

def ler_estatisticas_csv(caminho):
    import pandas as pd
    return pd.read_csv(caminho)

def ler_intermediacao_csv(caminho):
    import pandas as pd
    return pd.read_csv(caminho)

def natural_keys(text):
    # Divide em partes numéricas e não numéricas para ordenação natural
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]

def ordenar_nomes_arquivos_solucao(nomes_arquivos, pasta_testes):
    """
    Ordena a lista de nomes de arquivos de solução conforme a ordem dos arquivos .dat na pasta de testes.
    """
    arquivos_dat = [f for f in os.listdir(pasta_testes) if f.endswith('.dat')]
    def prioridade(nome):
        base = os.path.splitext(nome)[0]
        if base.startswith('BHW'):
            return (0, natural_keys(base))
        if base.startswith('CBMix'):
            return (1, natural_keys(base))
        if base.startswith('DI-NEARP'):
            return (2, natural_keys(base))
        if base.startswith('mggdb'):
            return (3, natural_keys(base))
        if base.startswith('mgval'):
            return (4, natural_keys(base))
        return (5, natural_keys(base))
    ordem = [os.path.splitext(f)[0] for f in sorted(arquivos_dat, key=prioridade)]
    def pos(nome):
        base = os.path.splitext(os.path.basename(nome))[0].replace('sol-', '')
        try:
            return ordem.index(base)
        except ValueError:
            return len(ordem)
    return sorted(nomes_arquivos, key=pos)