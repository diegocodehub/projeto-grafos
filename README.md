# Projeto: GRAFOS - Roteamento de Serviços em Grafos

Este projeto resolve o problema de roteamento de serviços em grafos (CARP - Capacitated Arc Routing Problem) utilizando heurísticas e metaheurísticas avançadas, com foco em eficiência e robustez. O código lê instâncias do problema a partir de arquivos `.dat`, gera soluções otimizadas e permite análise e visualização dos resultados.

## Funcionalidades Principais

- **Leitura estruturada de instâncias** a partir de arquivos `.dat` (pasta `testes/`).
- **Construção do grafo** como matriz de adjacência (usando `numpy`).
- **Geração de soluções** usando a heurística de Clarke & Wright e uma metaheurística Iterated Local Search (ILS) otimizada.
- **Exportação automática das soluções** para a pasta `resultados/`.
- **Testes unitários** para validação das soluções e desempenho.
- **Notebook de visualização** (`visualizar.ipynb`) para análise gráfica das soluções geradas.

## Estrutura do Projeto

- `main.py`: Executa todas as instâncias da pasta `testes/`, gera e salva as soluções otimizadas na pasta `resultados/`.
- `testes_unitarios.py`: Permite rodar e validar uma instância específica, útil para depuração e análise detalhada.
- `heuristica.py`: Implementa as heurísticas e metaheurísticas (Clarke & Wright, ILS, operadores locais, etc).
- `ler_escrever_arquivos.py`: Funções para leitura das instâncias e utilidades de entrada/saída.
- `resultados/`: Pasta onde as soluções geradas são salvas automaticamente.
- `testes/`: Pasta com as instâncias do problema no formato `.dat`.
- `visualizar.ipynb`: Notebook para visualizar graficamente as soluções salvas em `resultados/`.

## Como Usar

### 1. Gerar Soluções para Todas as Instâncias

Coloque os arquivos `.dat` das instâncias na pasta `testes/`.
Execute:

```bash
python main.py
```

As soluções serão salvas automaticamente na pasta `resultados/` com o prefixo `sol-`.

### 2. Rodar Teste Unitário em Uma Instância

Execute:

```bash
python testes_unitarios.py
```

Digite o nome do arquivo `.dat` desejado (ex: `BHW1.dat`) quando solicitado. O resultado será salvo em `resultados/` e exibido no terminal.

### 3. Visualizar Soluções Geradas

Abra o notebook `visualizar.ipynb` no Jupyter ou VSCode. Siga as instruções do notebook para carregar e visualizar graficamente as soluções da pasta `resultados/`.

## Sobre as Pastas

- **`testes/`**: Instâncias do problema (arquivos `.dat`).
- **`resultados/`**: Soluções geradas automaticamente pelo código, uma para cada instância.

## Requisitos

- Python 3.7+
- numpy
- psutil

Instale as dependências com:

```bash
pip install numpy psutil
```

## Observações

- O código utiliza uma metaheurística robusta (ILS) baseada em Clarke & Wright, com busca local e perturbação, garantindo soluções de alta qualidade.
- O notebook de visualização facilita a análise gráfica dos resultados.
- Os testes unitários permitem validar rapidamente o funcionamento para qualquer instância.
- As soluções são exportadas no formato esperado para avaliação ou uso posterior.

---

Para dúvidas ou sugestões, consulte o código-fonte ou entre em contato com o autor.
