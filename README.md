# Projeto: GRAFOS - ETAPA 2

Este projeto resolve o problema de roteamento de serviços em grafos (CARP - Capacitated Arc Routing Problem) utilizando heurísticas e metaheurísticas avançadas. O código lê instâncias do problema a partir de arquivos `.dat`, gera soluções otimizadas e permite análise e visualização dos resultados.

## Funcionalidades Principais

- **Leitura estruturada de instâncias** a partir de arquivos `.dat` (pasta `testes/`).
- **Construção do grafo** como matriz de adjacência (usando `numpy`).
- **Geração de soluções** usando a heurística de Clarke & Wright e uma metaheurística Iterated Local Search (ILS) otimizada.
- **Exportação automática das soluções** para a pasta `resultados/`.
- **Testes unitários** para validação das soluções e desempenho.
- **Notebook de visualização** (`visualizar.ipynb`) para análise gráfica das soluções geradas.

## Estrutura do Projeto

- `main.py`: Executa todas as instâncias da pasta `testes/`, identifica automaticamente se o grafo é pequeno (≤ 100 serviços) ou grande (> 100 serviços) e escolhe a abordagem adequada:
  - Pequeno: usa a metaheurística otimizada (ILS)
  - Grande: usa apenas Clarke & Wright
- `testes_unitarios.py`: Permite rodar e validar uma instância específica, útil para depuração e análise detalhada. Também identifica automaticamente o tipo de grafo e salva o resultado com o sufixo correspondente.
- `heuristica.py`: Implementa as heurísticas e metaheurísticas (Clarke & Wright, ILS, operadores locais, etc).
- `ler_escrever_arquivos.py`: Funções para leitura das instâncias e utilidades de entrada/saída.
- `resultados/`: Pasta onde as soluções geradas são salvas automaticamente, uma para cada instância processada.
- `testes/`: Pasta com as instâncias do problema no formato `.dat`.
- `visualizar.ipynb`: Notebook para visualizar graficamente as soluções salvas em `resultados/`.

## Como Usar

### 1. Gerar Soluções para Todas as Instâncias

Coloque os arquivos `.dat` das instâncias na pasta `testes/`.
Execute:

```powershell
python main.py
```

O código irá processar cada instância, escolher o método adequado e salvar a solução na pasta `resultados/` com o sufixo indicando o método utilizado.

### 2. Rodar Teste Unitário em Uma Instância

Execute:

```powershell
python testes_unitarios.py
```

Digite o nome do arquivo `.dat` desejado (ex: `BHW1.dat`) quando solicitado. O resultado será salvo em `resultados/` e exibido no terminal, com o sufixo indicando o método utilizado.

### 3. Visualizar Soluções Geradas

Abra o notebook `visualizar.ipynb` no Jupyter ou VSCode. Siga as instruções do notebook para carregar e visualizar graficamente as soluções da pasta `resultados/`.

## Sobre as Pastas

- **`testes/`**: Instâncias do problema (arquivos `.dat`).
- **`resultados/`**: Soluções geradas automaticamente pelo código, uma para cada instância. O nome do arquivo indica o método utilizado (`-ils.dat` ou `-cw.dat`).
- **`visualizar.ipynb`**: Notebook para visualização gráfica das soluções.

## Requisitos

- Python 3.7+
- numpy
- psutil

Instale as dependências com:

```powershell
pip install numpy psutil
```

## Observações

- O código utiliza uma metaheurística robusta (ILS) baseada em Clarke & Wright, com busca local e perturbação, garantindo soluções de alta qualidade para instâncias pequenas.
- Para instâncias grandes, utiliza-se apenas Clarke & Wright para garantir eficiência.
- O notebook de visualização facilita a análise gráfica das métricas da ETAPA 1.
- Os testes unitários permitem validar rapidamente o funcionamento para qualquer instância.
- As soluções são exportadas no formato esperado para avaliação ou uso posterior.

---

Para dúvidas ou sugestões, consulte o código-fonte ou entre em contato com o autor.
