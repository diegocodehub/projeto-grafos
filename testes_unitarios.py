"""
Arquivo principal do projeto CARP.
Realiza a leitura da instância, execução da heurística GRASP com 2-opt e gravação da solução.
"""
import os
import psutil
import time
from heurística import grasp_2opt_carp, construir_grafo, dijkstra_pred, caminho_mais_curto, matriz_menores_distancias
from ler_escrever_arquivos import ler_instancia

def teste_unitario_rodar_uma_instancia():
    nome = input('Digite o nome do arquivo .dat (ex: BHW1.dat): ').strip()
    pasta_testes = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testes')
    pasta_resultados = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
    os.makedirs(pasta_resultados, exist_ok=True)
    arquivo = os.path.join(pasta_testes, nome)
    if not os.path.exists(arquivo):
        print(f"Arquivo {arquivo} não encontrado!")
        return
    saida = os.path.join(pasta_resultados, f"sol-{os.path.splitext(os.path.basename(arquivo))[0]}.dat")
    v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr = ler_instancia(arquivo)
    # Construir dicionários de demanda e custo de serviço por id_servico
    custo_serv_dict = {}
    demanda_serv_dict = {}
    id_servico = 1
    for v, q in nos:
        custo_serv_dict[id_servico] = 0
        demanda_serv_dict[id_servico] = q
        id_servico += 1
    for (u, v), c, q in arestas_req:
        custo_serv_dict[id_servico] = c
        demanda_serv_dict[id_servico] = q
        id_servico += 1
    for (u, v), c, q in arcos_req:
        custo_serv_dict[id_servico] = c
        demanda_serv_dict[id_servico] = q
        id_servico += 1
    freq_mhz = psutil.cpu_freq().current
    freq_hz = freq_mhz * 1_000_000
    clock_inicio_total = time.perf_counter_ns()
    melhor_custo = float('inf')
    melhor_rotas = None
    melhor_tarefas = None
    total_tarefas = len(nos) + len(arestas_req) + len(arcos_req)
    num_exec = 30 if total_tarefas <= 33 else 20 if total_tarefas <= 70 else 10
    tempo_acumulado = 0
    for _ in range(num_exec):
        clock_ini_sol = time.perf_counter_ns()
        rotas, tarefas = grasp_2opt_carp(v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr)
        clock_fim_sol = time.perf_counter_ns()
        clock_sol = clock_fim_sol - clock_ini_sol
        tempo_acumulado += clock_sol
        if rotas is None or tarefas is None:
            continue
        custo_total = sum([custo_serv_dict.get(tarefas[tid]['id'], 0) for rota in rotas for tid in rota['tarefas']])
        if custo_total < melhor_custo:
            melhor_custo = custo_total
            melhor_rotas = rotas
            melhor_tarefas = tarefas
            clock_melhor_sol = tempo_acumulado
    if melhor_rotas is None or melhor_tarefas is None:
        print(f"NENHUMA SOLUÇÃO para {nome}")
        return
    clock_fim_total = time.perf_counter_ns()
    clock_total = clock_fim_total - clock_inicio_total
    ciclos_estimados_total = int(clock_total * (freq_hz / 1_000_000_000))
    ciclos_estimados_melhor_sol = int(clock_melhor_sol * (freq_hz / 1_000_000_000))
    grafo = construir_grafo(nos, arestas_req, arcos_req, arestas_nr, arcos_nr)
    matriz_pred = {u: dijkstra_pred(grafo, u)[1] for u in grafo}
    servicos_map = {}
    id_servico = 1
    for v, q in nos:
        servicos_map[(v, v)] = (id_servico, 'n')
        id_servico += 1
    for (u, v), c, q in arestas_req:
        servicos_map[(u, v)] = (id_servico, 'e')
        servicos_map[(v, u)] = (id_servico, 'e')
        id_servico += 1
    for (u, v), c, q in arcos_req:
        servicos_map[(u, v)] = (id_servico, 'a')
        id_servico += 1
    with open(saida, 'w', encoding='utf-8') as f:
        # Nova estrutura: lista de tarefas visitadas por rota
        todas_tarefas = set(range(1, id_servico))
        tarefas_atendidas = set()
        rotas_export = []
        custo_total_export = 0.0
        grafo = construir_grafo(nos, arestas_req, arcos_req, arestas_nr, arcos_nr)
        matriz_distancias = matriz_menores_distancias(nos, arestas_req, arcos_req, arestas_nr, arcos_nr)
        for rid, rota in enumerate(melhor_rotas, start=1):
            if not rota['tarefas']:
                continue
            detalhes = [f"(D 0,{v0},{v0})"]
            demanda_rota = 0
            for tid in rota['tarefas']:
                t = melhor_tarefas[tid]
                detalhes.append(f"(S {t['id']},{t['origem']},{t['destino']})")
                demanda_rota += demanda_serv_dict.get(t['id'], 0)
                tarefas_atendidas.add(t['id'])
            detalhes.append(f"(D 0,{v0},{v0})")
            num_visitas = len(detalhes)
            from heurística import custo_rota_especifica
            custo_rota = custo_rota_especifica(rota, melhor_tarefas, matriz_distancias)
            custo_total_export += custo_rota
            if demanda_rota > Q:
                print(f"[ERRO] Demanda da rota {rid} excede a capacidade Q={Q}!")
            rotas_export.append((rid, demanda_rota, custo_rota, num_visitas, detalhes))
        # Validação de cobertura
        if tarefas_atendidas != todas_tarefas:
            print(f"[ERRO] Nem todos os serviços obrigatórios foram atendidos!")
        # Exportação
        f.write(f"{custo_total_export:.2f}\n")
        f.write(f"{len(rotas_export)}\n")
        f.write(f"{ciclos_estimados_melhor_sol}\n")
        f.write(f"{ciclos_estimados_total}\n")
        for rid, demanda_rota, custo_rota, num_visitas, detalhes in rotas_export:
            prefixo = f"0 1 {rid} {demanda_rota} {custo_rota:.2f} {num_visitas}"
            f.write(prefixo + ' ' + ' '.join(detalhes) + "\n")
    print(f"Solução salva em {saida}")

if __name__ == '__main__':
    teste_unitario_rodar_uma_instancia()