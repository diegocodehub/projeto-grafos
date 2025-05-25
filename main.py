import sys
import time
import os
import psutil
from heuristica import (
    floyd_warshall, preparar_clientes, inicializar_rotas, juntar_rotas_iterativamente, info_serv, custo_serv_dict, custos_desloc
)
from ler_escrever_arquivos import ler_instancia, ordenar_nomes_arquivos_solucao


def main():
    pasta_testes = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testes')
    pasta_resultados = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
    os.makedirs(pasta_resultados, exist_ok=True)
    arquivos_dat = [f for f in os.listdir(pasta_testes) if f.endswith('.dat')]
    arquivos_dat = ordenar_nomes_arquivos_solucao(arquivos_dat, pasta_testes)
    freq_mhz = psutil.cpu_freq().current
    freq_hz = freq_mhz * 1_000_000
    for arquivo in arquivos_dat:
        instancia = os.path.join(pasta_testes, arquivo)
        saida = os.path.join(pasta_resultados, f"sol-{os.path.basename(instancia)}")
        # Início do clock1 (total, tempo real em ns)
        clock1_inicio = time.perf_counter_ns()
        v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr = ler_instancia(instancia)
        floyd_warshall(nos, arestas_req, arcos_req, arestas_nr, arcos_nr)
        clientes = preparar_clientes(nos, arestas_req, arcos_req)
        rotas = inicializar_rotas(clientes, v0)
        rotas.sort(key=lambda r: r['demanda_total'])
        # Início do clock2 (apenas heurística, tempo real em ns)
        clock2_inicio = time.perf_counter_ns()
        rotas = juntar_rotas_iterativamente(rotas, custos_desloc, v0, Q)
        clock2_fim = time.perf_counter_ns()
        # Monta saída e calcula custos
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
            # Soma deslocamento apenas para trechos que NÃO são serviços
            for i in range(len(rota) - 1):
                u, v = rota[i], rota[i+1]
                is_service = False
                for sid in seq:
                    info = info_serv.get(sid)
                    if info is not None:
                        _, i_s, j_s = info
                        if (u, v) == (i_s, j_s):
                            is_service = True
                            break
                if not is_service:
                    custo_d += custos_desloc.get((u, v), 0)
        custo_total = custo_d + custo_s
        num_rotas = len(rotas_finais)
        # clock1 para só antes de escrever o arquivo
        clock1_fim = time.perf_counter_ns()
        t_clock1 = int((clock1_fim - clock1_inicio) * (freq_hz / 1_000_000_000))
        t_clock2 = int((clock2_fim - clock2_inicio) * (freq_hz / 1_000_000_000))

        with open(saida, 'w', encoding='utf-8') as f:
            f.write(f"{custo_total}\n")
            f.write(f"{num_rotas}\n")
            f.write(f"{t_clock1}\n")  # clock 1: ciclos totais
            f.write(f"{t_clock2}\n")  # clock 2: ciclos heurística
            for rid, (rota, seq_ids) in enumerate(zip(rotas_finais, seqs_finais), start=1):
                demanda_rota = sum(custo_serv_dict.get(sid, 0) for sid in seq_ids)
                custo_rota = sum(custos_desloc.get((u, v), 0) for u, v in zip(rota, rota[1:])) + demanda_rota
                num_visitas = 2 + len(seq_ids)

                prefixo = f"0 1 {rid} {demanda_rota} {custo_rota} {num_visitas}"
                detalhes = ['(D 0,1,1)']
                for sid in seq_ids:
                    i, j = 0, 0
                    info = info_serv.get(sid)
                    if info is not None:
                        _, i, j = info
                    detalhes.append(f"(S {sid},{i},{j})")
                detalhes.append('(D 0,1,1)')

                f.write(prefixo + ' ' + ' '.join(detalhes) + "\n")

if __name__ == '__main__':
    main()