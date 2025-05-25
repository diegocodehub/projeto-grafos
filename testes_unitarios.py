"""
Arquivo principal do projeto CARP.
Lê uma instância do problema a partir de um arquivo .dat, executa a heurística e salva a solução em um arquivo de saída.
"""
import sys
import time
import os
import psutil
from heuristica import (
    floyd_warshall, preparar_clientes, inicializar_rotas, juntar_rotas_iterativamente, info_serv, custo_serv_dict, custos_desloc, demanda_serv_dict
)
from ler_escrever_arquivos import ler_instancia

if __name__ == '__main__':
    nome_arquivo = input('Digite o nome do arquivo .dat (ex: BHW1.dat): ').strip()
    pasta_testes = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testes')
    pasta_resultados = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
    os.makedirs(pasta_resultados, exist_ok=True)
    instancia = os.path.join(pasta_testes, nome_arquivo)
    saida = os.path.join(pasta_resultados, f"sol-{os.path.basename(instancia)}")
    freq_mhz = psutil.cpu_freq().current
    freq_hz = freq_mhz * 1_000_000
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
    # Garante que cada serviço é contado apenas uma vez (por rota)
    todos_servicos_atendidos = set()
    for rota, seq in zip(rotas_finais, seqs_finais):
        visitados = set()
        for sid in seq:
            if sid not in todos_servicos_atendidos:
                custo_s += custo_serv_dict.get(sid, 0)
                todos_servicos_atendidos.add(sid)
            if sid not in visitados:
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

    # --- VERIFICAÇÃO DE RESTRIÇÕES ---
    servicos_esperados = set(info_serv.keys())
    servicos_atendidos = set()
    for seq in seqs_finais:
        for sid in set(seq):
            servicos_atendidos.add(sid)
    if servicos_esperados != servicos_atendidos:
        print('ERRO: Serviços não atendidos ou atendidos mais de uma vez.')
    for idx, seq in enumerate(seqs_finais):
        demanda_rota = sum([custo_serv_dict.get(sid, 0) for sid in set(seq)])
        if demanda_rota > Q:
            print(f'ERRO: Rota {idx+1} excede capacidade ({demanda_rota}>{Q})')

    # --- DEPURAÇÃO DE COBERTURA DE SERVIÇOS ---
    print('DEBUG: Serviços esperados:', sorted(servicos_esperados))
    print('DEBUG: Serviços atendidos:', sorted(servicos_atendidos))
    faltando = servicos_esperados - servicos_atendidos
    extras = servicos_atendidos - servicos_esperados
    if faltando:
        print('DEBUG: Faltando:', sorted(faltando))
    if extras:
        print('DEBUG: Extras:', sorted(extras))

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
            demanda_rota = sum(demanda_serv_dict.get(sid, 0) for sid in set(seq_ids))
            custo_rota = 0
            # Soma deslocamento apenas para trechos que NÃO são serviços
            for i in range(len(rota) - 1):
                u, v = rota[i], rota[i+1]
                is_service = False
                for sid in set(seq_ids):
                    info = info_serv.get(sid)
                    if info is not None:
                        _, i_s, j_s = info
                        if (u, v) == (i_s, j_s):
                            is_service = True
                            break
                if not is_service:
                    custo_rota += custos_desloc.get((u, v), 0)
            custo_rota += sum(custo_serv_dict.get(sid, 0) for sid in set(seq_ids))
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
    print(f'Solução salva em: {saida}')
