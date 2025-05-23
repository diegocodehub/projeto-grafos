"""
Arquivo de testes unitários simples para funções principais do projeto CARP.
Utiliza apenas asserts para facilitar execução e compreensão.
"""
from métricas import extrair_dados_instancia, densidade, calcula_graus
import numpy as np

def test_extrair_dados_instancia():
    linhas = [
        'C 1', 'C 2', 'V 2', 'Q 10', 'D 1', 'N 3', 'E 2', 'A 1', 'VReq 0', 'EReq 1', 'AReq 0', '',
        'N1 5 0', '', 'ReE.', 'E 1 2 3 4 0', '', 'EDGE', '', 'ReA.', '', 'ARC'
    ]
    dados = extrair_dados_instancia(linhas)
    assert dados['qtd_vertices'] == 3
    assert dados['capacidade'] == 10
    assert len(dados['arestas_req']) == 1
    assert dados['arestas_req'][0][:3] == (1, 2, 3)
    print('test_extrair_dados_instancia OK')

def test_densidade():
    dens = densidade(4, 3, 2)
    assert abs(dens - ((3+2)/((4*3/2)+(4*3)))) < 1e-6
    print('test_densidade OK')

def test_calcula_graus():
    linhas = [
        'C 1', 'C 2', 'V 2', 'Q 10', 'D 1', 'N 3', 'E 2', 'A 1', 'VReq 0', 'EReq 1', 'AReq 0', '',
        'N1 5 0', '', 'ReE.', 'E 1 2 3 4 0', '', 'EDGE', '', 'ReA.', '', 'ARC'
    ]
    dados = extrair_dados_instancia(linhas)
    graus = calcula_graus(dados)
    assert isinstance(graus, list)
    assert graus[0][0] == 1
    print('test_calcula_graus OK')

if __name__ == '__main__':
    test_extrair_dados_instancia()
    test_densidade()
    test_calcula_graus()
    print('Todos os testes passaram!')
