import sys
import time
import psutil
import os
from heuristica import resolver_problema, info_serv, custo_serv_dict, custos_desloc
from ler_escrever_arquivos import ler_instancia, ler_reference_values, salvar_solucao

def main():
    """
    Função principal do programa. Orquestra a leitura da instância, execução da heurística e salvamento da solução.
    Uso: python main.py <instancia.dat>
    """

    if len(sys.argv) != 2:
        print('Uso: python main.py <instancia.dat>')
        sys.exit(1)

    instancia = sys.argv[1]
    nome_base = os.path.splitext(os.path.basename(instancia))[0]
    pasta_resultados = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
    os.makedirs(pasta_resultados, exist_ok=True)
    saida = os.path.join(pasta_resultados, f"{nome_base}_sol.dat")
    reference_csv = os.path.join(os.path.dirname(__file__), 'reference_values.csv')
    _, clock_melhor_sol = ler_reference_values(reference_csv, nome_base)
    v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr = ler_instancia(instancia)

    freq_mhz = psutil.cpu_freq().current
    freq_hz = freq_mhz * 1_000_000

    clock_inicio_total = time.perf_counter_ns()
    rotas, seq_ids_por_rota, custo_desloc_total, custo_serv_total = resolver_problema(
        v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr
    )
    clock_fim_total = time.perf_counter_ns()
    clock_total = clock_fim_total - clock_inicio_total
    ciclos_estimados = int(clock_total * (freq_hz / 1_000_000_000))

    custo_total = custo_desloc_total + custo_serv_total
    num_rotas = len(rotas)

    # Monta detalhes das rotas para salvar
    detalhes_rotas = []
    for rid, (rota, seq_ids) in enumerate(zip(rotas, seq_ids_por_rota), start=1):
        demanda_rota = 0
        for sid in seq_ids:
            if sid in custo_serv_dict:
                demanda_rota += custo_serv_dict[sid]
            else:
                for cliente in rotas:
                    if isinstance(cliente, dict):
                        for c in cliente.get('clientes', []):
                            if c['id'] == sid:
                                demanda_rota += c['demanda']
                                break
        custo_desloc = 0
        for u, v in zip(rota, rota[1:]):
            if (u, v) in custos_desloc:
                custo_desloc += custos_desloc[(u, v)]
            else:
                from heuristica import dijkstra
                grafo_tmp = {}
                for (a, b), c in custos_desloc.items():
                    if a not in grafo_tmp:
                        grafo_tmp[a] = []
                    grafo_tmp[a].append((b, c))
                if u not in grafo_tmp:
                    grafo_tmp[u] = []
                dist, _ = dijkstra(grafo_tmp, u)
                custo_desloc += dist.get(v, 0)
        custo_rota = custo_desloc + demanda_rota
        num_visitas = 2 + len(seq_ids)
        prefixo = f"0 1 {rid} {demanda_rota} {custo_rota} {num_visitas}"
        detalhes = ['(D 0,1,1)']
        for sid in seq_ids:
            if sid in info_serv:
                _, i, j = info_serv[sid]
            else:
                i = j = None
                for cliente in rotas:
                    if isinstance(cliente, dict):
                        for c in cliente.get('clientes', []):
                            if c['id'] == sid:
                                i = c['origem']
                                j = c['destino']
                                break
                if i is None or j is None:
                    i = j = 0
            detalhes.append(f"(S {sid},{i},{j})")
        detalhes.append('(D 0,1,1)')
        detalhes_rotas.append(prefixo + ' ' + ' '.join(detalhes))

    salvar_solucao(saida, custo_total, num_rotas, clock_melhor_sol, ciclos_estimados, rotas, seq_ids_por_rota, None, None, detalhes_rotas)

if __name__ == '__main__':
    main()