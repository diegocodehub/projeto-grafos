def construir_rotas_iniciais(servicos, deposito, matriz_distancias, capacidade):
    rotas = []
    demandas = []
    for serv in servicos:
        demanda = serv['demanda']
        if demanda > capacidade:
            raise ValueError(f"Serviço {serv['id_servico']} demanda maior que capacidade do veículo!")
        rotas.append([serv])
        demandas.append(demanda)
    return rotas, demandas

def calcular_savings(rotas, matriz_distancias, deposito):
    savings = []
    n = len(rotas)
    for i in range(n):
        serv_i = rotas[i][0]
        origem_i = serv_i['origem']
        destino_i = serv_i['destino']

        for j in range(i+1, n):
            serv_j = rotas[j][0]
            origem_j = serv_j['origem']
            destino_j = serv_j['destino']

            s = (matriz_distancias[deposito][origem_i] +
                 matriz_distancias[destino_j][deposito] -
                 matriz_distancias[destino_i][origem_j])
            savings.append((s, i, j))
    savings.sort(key=lambda x: x[0], reverse=True)
    return savings

def tentar_fundir_rotas(rotas, demandas, idx_i, idx_j, capacidade):
    rota_i = rotas[idx_i]
    rota_j = rotas[idx_j]

    demanda_total = demandas[idx_i] + demandas[idx_j]
    if demanda_total > capacidade:
        return False

    ids_i = set(s['id_servico'] for s in rota_i)
    ids_j = set(s['id_servico'] for s in rota_j)

    if ids_i.intersection(ids_j):
        return False

    rotas[idx_i] = rota_i + rota_j
    demandas[idx_i] = demanda_total

    rotas[idx_j] = []
    demandas[idx_j] = 0
    return True



def algoritmo_clarke_wright(servicos, deposito, matriz_distancias, capacidade):
    rotas, demandas = construir_rotas_iniciais(servicos, deposito, matriz_distancias, capacidade)
    savings = calcular_savings(rotas, matriz_distancias, deposito)

    for s, i, j in savings:
        if rotas[i] and rotas[j]:
            tentar_fundir_rotas(rotas, demandas, i, j, capacidade)

    # Remove rotas vazias
    rotas = [r for r in rotas if r]
    return rotas
def salvar_solucao(
    nome_arquivo,
    rotas,
    matriz_distancias,
    deposito=0,
    tempo_referencia_execucao=0,
    tempo_referencia_solucao=0
):
    custo_total_solucao = 0
    total_rotas = len(rotas)
    linhas_rotas = []

    for idx_rota, rota in enumerate(rotas, start=1):
        servicos_unicos = {}
        demanda_rota = 0
        custo_servico_rota = 0
        custo_transporte_rota = 0

        destinos = []
        for serv in rota:
            id_s = serv["id_servico"]
            if id_s not in servicos_unicos:
                servicos_unicos[id_s] = serv
                demanda_rota += serv["demanda"]
                custo_servico_rota += serv["custo_servico"]
            destinos.append(serv["destino"])

        if destinos:
            custo_transporte_rota += matriz_distancias[deposito][destinos[0]]
            for i in range(len(destinos) - 1):
                custo_transporte_rota += matriz_distancias[destinos[i]][destinos[i + 1]]
            custo_transporte_rota += matriz_distancias[destinos[-1]][deposito]

        custo_rota = custo_servico_rota + custo_transporte_rota
        custo_total_solucao += custo_rota

        total_visitas = 2 + len(servicos_unicos)

        linha = f"0 1 {idx_rota} {demanda_rota} {custo_rota} {total_visitas} (D {deposito},1,1)"

        servicos_impressos = set()
        for serv in rota:
            id_s = serv["id_servico"]
            if id_s in servicos_impressos:
                continue
            servicos_impressos.add(id_s)
            linha += f" (S {id_s},{serv['origem']},{serv['destino']})"

        linha += f" (D {deposito},1,1)"
        linhas_rotas.append(linha)

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(f"{custo_total_solucao}\n")
        f.write(f"{total_rotas}\n")
        f.write(f"{tempo_referencia_execucao}\n")
        f.write(f"{tempo_referencia_solucao}\n")
        for linha in linhas_rotas:
            f.write(linha + "\n")

    print(f"Solução salva em '{nome_arquivo}' com {total_rotas} rotas e custo total {custo_total_solucao}.")
import random
import copy

def two_opt(route, distance_matrix, deposit, max_iter=10):
    if len(route) < 3:
        return route, False
    best = route[:]
    improved = False
    best_cost = route_cost(route, distance_matrix, deposit)
    count = 0
    while count < max_iter:
        found = False
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                new_route = best[:i] + best[i:j][::-1] + best[j:]
                new_cost = route_cost(new_route, distance_matrix, deposit)
                if new_cost < best_cost:
                    best = new_route
                    best_cost = new_cost
                    improved = True
                    found = True
        if not found:
            break
        count += 1
    return best, improved

def route_cost(route, distance_matrix, deposit):
    if not route:
        return 0
    cost = distance_matrix[deposit][route[0]['origem']]
    for i in range(len(route) - 1):
        cost += distance_matrix[route[i]['destino']][route[i+1]['origem']]
    cost += distance_matrix[route[-1]['destino']][deposit]
    cost += sum(s['custo_servico'] for s in route)
    return cost

def reallocation(routes, demands, capacity, distance_matrix, deposit):
    best_routes = copy.deepcopy(routes)
    best_demands = demands[:]
    best_cost = sum(route_cost(r, distance_matrix, deposit) for r in routes)
    improved = False
    for i, route_from in enumerate(routes):
        for j, route_to in enumerate(routes):
            if i == j or not route_from:
                continue
            for idx, serv in enumerate(route_from):
                if demands[j] + serv['demanda'] <= capacity:
                    new_routes = copy.deepcopy(routes)
                    new_demands = demands[:]
                    new_routes[j].append(serv)
                    new_demands[j] += serv['demanda']
                    del new_routes[i][idx]
                    new_demands[i] -= serv['demanda']
                    if not new_routes[i]:
                        continue
                    new_cost = sum(route_cost(r, distance_matrix, deposit) for r in new_routes)
                    if new_cost < best_cost:
                        best_routes = new_routes
                        best_demands = new_demands
                        best_cost = new_cost
                        improved = True
    return best_routes, best_demands, improved

def swap(routes, demands, capacity, distance_matrix, deposit):
    best_routes = copy.deepcopy(routes)
    best_demands = demands[:]
    best_cost = sum(route_cost(r, distance_matrix, deposit) for r in routes)
    improved = False
    for i, route_a in enumerate(routes):
        for j, route_b in enumerate(routes):
            if i >= j:
                continue
            for idx_a, serv_a in enumerate(route_a):
                for idx_b, serv_b in enumerate(route_b):
                    if (demands[i] - serv_a['demanda'] + serv_b['demanda'] <= capacity and
                        demands[j] - serv_b['demanda'] + serv_a['demanda'] <= capacity):
                        new_routes = copy.deepcopy(routes)
                        new_demands = demands[:]
                        new_routes[i][idx_a], new_routes[j][idx_b] = new_routes[j][idx_b], new_routes[i][idx_a]
                        new_demands[i] = new_demands[i] - serv_a['demanda'] + serv_b['demanda']
                        new_demands[j] = new_demands[j] - serv_b['demanda'] + serv_a['demanda']
                        new_cost = sum(route_cost(r, distance_matrix, deposit) for r in new_routes)
                        if new_cost < best_cost:
                            best_routes = new_routes
                            best_demands = new_demands
                            best_cost = new_cost
                            improved = True
    return best_routes, best_demands, improved

def random_perturbation(routes, demands, capacity):
    routes = copy.deepcopy(routes)
    demands = demands[:]
    non_empty = [i for i, r in enumerate(routes) if r]
    if len(non_empty) < 2:
        return routes, demands
    i, j = random.sample(non_empty, 2)
    if not routes[i]:
        return routes, demands
    idx = random.randrange(len(routes[i]))
    serv = routes[i][idx]
    if demands[j] + serv['demanda'] <= capacity:
        routes[j].append(serv)
        demands[j] += serv['demanda']
        del routes[i][idx]
        demands[i] -= serv['demanda']
    return routes, demands

def iterated_local_search(initial_routes, demands, capacity, distance_matrix, deposit, iterations=50):
    best_routes = copy.deepcopy(initial_routes)
    best_demands = demands[:]
    best_cost = sum(route_cost(r, distance_matrix, deposit) for r in best_routes)
    current_routes = copy.deepcopy(initial_routes)
    current_demands = demands[:]
    for _ in range(iterations):
        # Local search: 2-opt
        for i, route in enumerate(current_routes):
            improved = True
            inner = 0
            while improved and inner < 10:
                new_route, improved = two_opt(route, distance_matrix, deposit)
                if improved:
                    current_routes[i] = new_route
                inner += 1
        # Local search: reallocation
        current_routes, current_demands, improved = reallocation(current_routes, current_demands, capacity, distance_matrix, deposit)
        # Local search: swap
        current_routes, current_demands, improved = swap(current_routes, current_demands, capacity, distance_matrix, deposit)
        # Evaluate
        current_cost = sum(route_cost(r, distance_matrix, deposit) for r in current_routes)
        if current_cost < best_cost:
            best_routes = copy.deepcopy(current_routes)
            best_demands = current_demands[:]
            best_cost = current_cost
        # Perturbation
        current_routes, current_demands = random_perturbation(current_routes, current_demands, capacity)
    return best_routes, best_demands

def two_opt_simple(route, distance_matrix, depot):
    if len(route) < 3:
        return route
    best = route[:]
    best_cost = route_cost(best, distance_matrix, depot)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                new_route = best[:i] + best[i:j][::-1] + best[j:]
                new_cost = route_cost(new_route, distance_matrix, depot)
                if new_cost < best_cost:
                    best = new_route
                    best_cost = new_cost
                    improved = True
        if improved:
            break
    return best

def total_solution_cost(routes, distance_matrix, depot):
    return sum(route_cost(r, distance_matrix, depot) for r in routes)

def perturbation(routes, capacity):
    # Remove 2-3 random services and reinsert into other routes
    routes = copy.deepcopy(routes)
    all_services = [(i, idx) for i, r in enumerate(routes) for idx in range(len(r))]
    if len(all_services) < 3:
        return routes
    num_remove = min(3, len(all_services))
    remove_indices = random.sample(all_services, num_remove)
    removed = []
    for i, idx in sorted(remove_indices, reverse=True):
        removed.append(routes[i][idx])
        del routes[i][idx]
    # Reinsert removed services into random routes (with capacity check)
    for serv in removed:
        possible = [i for i, r in enumerate(routes) if sum(s['demanda'] for s in r) + serv['demanda'] <= capacity]
        if not possible:
            # If nowhere fits, create a new route
            routes.append([serv])
        else:
            i = random.choice(possible)
            insert_pos = random.randint(0, len(routes[i]))
            routes[i].insert(insert_pos, serv)
    # Remove empty routes
    routes = [r for r in routes if r]
    return routes

def iterated_local_search_optimized(servicos, distance_matrix, capacity, depot, iterations=30):
    from heuristica import algoritmo_clarke_wright
    # Initial solution
    routes = algoritmo_clarke_wright(servicos, depot, distance_matrix, capacity)
    # 2-opt on each route
    routes = [two_opt_simple(r, distance_matrix, depot) for r in routes]
    best_routes = copy.deepcopy(routes)
    best_cost = total_solution_cost(best_routes, distance_matrix, depot)
    for _ in range(min(iterations, 10)):
        # Perturbation
        perturbed = perturbation(routes, capacity)
        # 2-opt on perturbed solution
        perturbed = [two_opt_simple(r, distance_matrix, depot) for r in perturbed]
        cost = total_solution_cost(perturbed, distance_matrix, depot)
        if cost < best_cost:
            best_routes = copy.deepcopy(perturbed)
            best_cost = cost
        routes = copy.deepcopy(perturbed)
    return best_routes