import sys
import time
from heuristica import resolver_problema, info_serv, custo_serv_dict, custos_desloc


def ler_instancia(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = [l.rstrip() for l in f if l.strip()]

        # Cabeçalhos fixos
        capacidade   = int(linhas[3].split()[-1])
        deposito     = int(linhas[4].split()[-1])
        qtd_v_req    = int(linhas[8].split()[-1])
        qtd_e_req    = int(linhas[9].split()[-1])
        qtd_a_req    = int(linhas[10].split()[-1])

        # Seção ReN.
        i = 12
        nos = []
        for _ in range(qtd_v_req):
            partes = linhas[i].split()
            v = int(partes[0][1:]); q = int(partes[1])
            nos.append((v, q)); i += 1

        # Seção ReE. (arestas requeridas)
        while not linhas[i].startswith('ReE.'):
            i += 1
        i += 1
        arestas_req = []
        for _ in range(qtd_e_req):
            p = linhas[i].split()
            o, d, c, qv = map(int, p[1:5])
            arestas_req.append(((o, d), c, qv)); i += 1

        # Seção EDGE (arestas não requeridas)
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

        # Seção ReA. (arcos requeridos)
        while not linhas[i].startswith('ReA.'):
            i += 1
        i += 1
        arcos_req = []
        for _ in range(qtd_a_req):
            p = linhas[i].split()
            o, d, c, qv = map(int, p[1:5])
            arcos_req.append(((o, d), c, qv)); i += 1

        # Seção ARC (arcos não requeridos)
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
        print(f"Erro ao ler instância: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print('Uso: python main.py <instancia.dat> <sol-nome.dat>')
        sys.exit(1)

    instancia, saida = sys.argv[1], sys.argv[2]
    v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr = ler_instancia(instancia)

    inicio = time.process_time()
    rotas, seq_ids_por_rota, custo_desloc_total, custo_serv_total = resolver_problema(
        v0, Q, arestas_req, arcos_req, nos, arestas_nr, arcos_nr
    )
    fim = time.process_time()

    custo_total = custo_desloc_total + custo_serv_total
    num_rotas = len(rotas)
    t_clock = int((fim - inicio) * 1e6)

    # Escreve solução em arquivo
    with open(saida, 'w', encoding='utf-8') as f:
        f.write(f"{custo_total}\n")
        f.write(f"{num_rotas}\n")
        f.write(f"{t_clock}\n")
        f.write(f"{t_clock}\n")

        for rid, (rota, seq_ids) in enumerate(zip(rotas, seq_ids_por_rota), start=1):
            demanda_rota = sum(custo_serv_dict[sid] for sid in seq_ids)
            custo_rota = sum(custos_desloc[(u, v)] for u, v in zip(rota, rota[1:])) + demanda_rota
            num_visitas = 2 + len(seq_ids)

            prefixo = f"0 1 {rid} {demanda_rota} {custo_rota} {num_visitas}"
            detalhes = ['(D 0,1,1)']
            for sid in seq_ids:
                _, i, j = info_serv[sid]
                detalhes.append(f"(S {sid},{i},{j})")
            detalhes.append('(D 0,1,1)')

            f.write(prefixo + ' ' + ' '.join(detalhes) + "\n")

if __name__ == '__main__':
    main()