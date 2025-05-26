# Projeto: GRAFOS - ETAPA 2

Este projeto resolve o problema de roteamento de serviços em grafos (CARP - Capacitated Arc Routing Problem) utilizando heurísticas e metaheurísticas avançadas. O código lê instâncias do problema a partir de arquivos `.dat`, gera soluções otimizadas e permite análise e visualização dos resultados.

---

## Descrição Geral

O objetivo é processar instâncias de grafos (em arquivos `.dat`), calcular rotas otimizadas para serviços em vértices, arestas e arcos, e exportar as soluções em formato padronizado. O projeto utiliza o algoritmo de **Clarke & Wright Savings** e uma metaheurística Iterated Local Search (ILS) para instâncias pequenas, escolhendo automaticamente a abordagem mais eficiente conforme o tamanho do problema.

---

## Estrutura dos Arquivos e Pastas

- `main.py`: Executa todas as instâncias da pasta `instancias/`, identifica automaticamente se o grafo é pequeno (≤ 100 serviços) ou grande (> 100 serviços) e escolhe a abordagem adequada:
  - Pequeno: usa a metaheurística otimizada (ILS)
  - Grande: usa apenas Clarke & Wright
  - O nome do arquivo de saída indica o método: `-ils.dat` (ILS) ou `-cw.dat` (Clarke & Wright)
- `testes_unitarios.py`: Permite rodar e validar uma instância específica, útil para depuração e análise detalhada. Também identifica automaticamente o tipo de grafo e salva o resultado com o sufixo correspondente.
- `heuristica.py`: Implementa as heurísticas e metaheurísticas (Clarke & Wright, ILS, operadores locais, etc).
- `ler_escrever_arquivos.py`: Funções para leitura das instâncias e utilidades de entrada/saída.
- `resultados/`: Pasta onde as soluções geradas são salvas automaticamente, uma para cada instância processada. O nome do arquivo indica o método utilizado (`-ils.dat` ou `-cw.dat`).
- `instancias/`: Pasta com as instâncias do problema no formato `.dat`.
- `visualizar.ipynb`: Notebook para visualizar graficamente as soluções salvas em `resultados/`.

---

## Como Executar

### 1. Pré-requisitos

- Python 3.7+
- numpy
- psutil

Instale as dependências com:

```powershell
pip install numpy psutil
```

### 2. Gerar Soluções para Todas as Instâncias

Coloque os arquivos `.dat` das instâncias na pasta `instancias/`.
Execute:

```powershell
python main.py
```

O código irá processar cada instância, escolher o método adequado e salvar a solução na pasta `resultados/` com o sufixo indicando o método utilizado.

### 3. Rodar Teste Unitário em Uma Instância

Execute:

```powershell
python testes_unitarios.py
```

Digite o nome do arquivo `.dat` desejado (ex: `BHW1.dat`) quando solicitado. O resultado será salvo em `resultados/` e exibido no terminal, com o sufixo indicando o método utilizado.

### 4. Visualizar Soluções Geradas

Abra o notebook `visualizar.ipynb` no Jupyter ou VSCode. Siga as instruções do notebook para carregar e visualizar graficamente as soluções da pasta `resultados/`.

---

## Funcionalidades

- Leitura completa de arquivos `.dat` estruturados.
- Construção de matrizes de menor distância entre pares (via algoritmo de Floyd-Warshall).
- Execução do algoritmo **Clarke-Wright Savings** e da metaheurística ILS para instâncias pequenas.
- Exportação automática das soluções em formato padronizado.
- Cálculo de métricas de tempo em ciclos de CPU.
- Visualização gráfica das soluções via notebook.

---

## Formato dos Arquivos

### Entrada (`.dat`)

- Arquivos `.dat` devem seguir o padrão de instâncias CARP, com campos separados por TAB e blocos para nós, arestas, arcos e demandas.
- Veja exemplos na pasta `instancias/`.

### Saída (`resultados/`)

- Cada arquivo de solução contém:
  - Custo total da solução
  - Total de rotas
  - Tempos de referência de execução e solução
  - Descrição detalhada das rotas

Exemplo de saída:

```
337
6
14561498
64474
0 1 1 5 61  7 (D 0,1,1) (S 21,1,7) (S 14,7,8) (S 28,8,10) (S 3,10,10) (S 17,10,9) (D 0,1,1)
...
```

---

## Observações

- O código utiliza uma metaheurística robusta (ILS) baseada em Clarke & Wright, com busca local e perturbação, garantindo soluções de alta qualidade para instâncias pequenas.
- Para instâncias grandes, utiliza-se apenas Clarke & Wright para garantir eficiência.
- O notebook de visualização facilita a análise gráfica dos resultados.
- Os testes unitários permitem validar rapidamente o funcionamento para qualquer instância.
- As soluções são exportadas no formato esperado para avaliação ou uso posterior.

---

Para dúvidas ou sugestões, consulte o código-fonte ou entre em contato com os autores.
